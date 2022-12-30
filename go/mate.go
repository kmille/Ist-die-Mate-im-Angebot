package main

import (
	"bufio"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"strings"

	html "github.com/levigross/exp-html"
	gomail "gopkg.in/mail.v2"
)

const tegut_tmp_file = "/tmp/.tegut_tmp.pdf"

var mailBody = "Mate Checker\n\n"

const mailSubject = "Ist die Mate schon da?"

func handle_error(err error) {
	if err != nil {
		log(err.Error() + "\n")
		send_mail()
		os.Exit(1)
	}
}

type PriceData struct {
	Price        string
	RegularPrice string
}

type Offer struct {
	Title     string
	PriceData PriceData
}

type Category struct {
	Offers []Offer
}

type APIResponse struct {
	Categories []Category
}

func log(text string) {
	fmt.Printf("%s", text)
	mailBody = mailBody + text
}

func do_rewe() {
	log("Rewe Angebote\n")
	resp, err := http.Get("https://mobile-api.rewe.de/api/v3/all-offers?marketCode=240070")
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	handle_error(err)
	if resp.StatusCode != 200 {
		handle_error(errors.New(string(body)))
	}
	var api APIResponse
	err = json.Unmarshal(body, &api)
	handle_error(err)
	for _, category := range api.Categories {
		for _, offer := range category.Offers {
			if strings.Contains(strings.ToLower(offer.Title), "mate") &&
				!strings.Contains(strings.ToLower(offer.Title), "tomate") {
				log(offer.Title + " (" + offer.PriceData.Price + " " + offer.PriceData.RegularPrice + ") \n")
			}
		}
	}
}

func do_tegut() {
	log("\nTegut Angebote\n")
	downloadLink := getAngeboteDownloadLink()
	log("Angebote " + downloadLink + "\n")
	downloadTegutAngebotePDF(downloadLink)

	cmd := exec.Command("pdfgrep", "-i", "mate", tegut_tmp_file)
	out, err := cmd.Output()
	handle_error(err)
	scanner := bufio.NewScanner(strings.NewReader(string(out)))
	for scanner.Scan() {
		text := strings.TrimSpace(scanner.Text())
		if !strings.Contains(strings.ToLower(text), "tomate") {
			log(text + "\n")
		}
	}
	os.Remove(tegut_tmp_file)
}

func parseHTML(bodyString string) (string, error) {
	reader := strings.NewReader(bodyString)
	tokenizer := html.NewTokenizer(reader)
	for {
		tt := tokenizer.Next()
		if tt == html.ErrorToken {
			return "", tokenizer.Err()
		}
		tag, hasAttr := tokenizer.TagName()
		if string(tag) == "a" && hasAttr {
			for {
				attrKey, attrValue, moreAttr := tokenizer.TagAttr()
				if string(attrKey) == "href" && strings.Contains(string(attrValue), ".pdf") {
					return string(attrValue), nil
				}
				if !moreAttr {
					break
				}
			}
		}
	}
	return "", errors.New("Could not get download url from html code")
}

func getAngeboteDownloadLink() string {
	url := "https://www.tegut.com/angebote-produkte/angebote.html?offers%5Bstore%5D=2464"
	contentType := "application/x-www-form-urlencoded"
	postData := strings.NewReader("type=9267&contentid=66663&mktoolsAjaxRequest=true&page=&useHistory=true")

	resp, err := http.Post(url, contentType, postData)
	handle_error(err)
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		handle_error(fmt.Errorf("Could not get link to Tegut Angebote (statusCode=%d)\n", resp.StatusCode))
	}
	bodyBytes, err := io.ReadAll(resp.Body)
	handle_error(err)
	bodyString := string(bodyBytes)
	url, err = parseHTML(bodyString)
	handle_error(err)
	return url
}

func downloadTegutAngebotePDF(url string) {
	//fmt.Println("Downloading Tegut Angebote")
	resp, err := http.Get(url)
	handle_error(err)
	defer resp.Body.Close()

	out, err := os.Create(tegut_tmp_file)
	handle_error(err)
	defer out.Close()
	_, err = io.Copy(out, resp.Body)
	handle_error(err)

}

func send_mail() {
	from := ""
	password := ""
	to := ""

	m := gomail.NewMessage()
	m.SetHeader("From", from)
	m.SetHeader("To", to)
	m.SetHeader("Subject", mailSubject)
	m.SetBody("text/plain", mailBody)

	d := gomail.NewDialer("beeftraeger.wurbz.de", 465, from, password)
	d.RetryFailure = false
	err := d.DialAndSend(m)
	handle_error(err)
	fmt.Println("mail sent")
}

func main() {
	do_rewe()
	do_tegut()
	send_mail()
	fmt.Println("done")

}

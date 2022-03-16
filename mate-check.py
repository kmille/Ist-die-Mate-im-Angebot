#!/usr/bin/env python3
import os
import arrow
import requests
import json
import subprocess

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

headers = {"User-Agent": "Firefox auf Windows. Ganz bestimmt."}

tmp_file_tegut = "tegut-angebote.pdf"

username = ""
password = ""
smtphost = "beeftraeger.wurbz.de:465"
smtpfrom = username
smtpto = ""


def get_tegut_angebot_url():
    now = arrow.now()
    return f"https://static.tegut.com/fileadmin/tegut_upload/Dokumente/Aktuelle_Flugbl%C3%A4tter/tegut-prospekt-kw-{now.week:02}-2022-Hessen-Niedersachsen-Rheinland-Pfalz.pdf"


def do_tegut():
    print("Checking Tegut Angeote")
    resp = requests.get(get_tegut_angebot_url(), headers=headers)
    assert resp.status_code == 200
    with open(tmp_file_tegut, "wb") as f:
        f.write(resp.content)
    print(f"Downloaded Tegut Angebote to {tmp_file_tegut}")
    p = subprocess.Popen(["pdfgrep", "-i", "mate", tmp_file_tegut], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    assert p.returncode == 0
    stdout, stderr = p.communicate()
    os.remove(tmp_file_tegut)
    print(stdout.decode())
    return stdout.decode()


def do_rewe():
    """
        240817: REWE Südmarkt GmbH Mitte, Leydhecker Str. 16 None, 64293 Darmstadt
        241176: REWE Michael Weisbrod oHG, Pallaswiesenstr. 70-72 None, 64293 Darmstadt
        240660: REWE Markt GmbH, Europaplatz 2 None, 64293 Darmstadt
        240573: REWE Markt GmbH, Berliner Allee 59 None, 64295 Darmstadt
        862193: REWE Regiemarkt GmbH, Gutenbergstraße 3-15 / Loop5 None, 64331 Weiterstadt / Riedbahn
        240270: REWE Markt GmbH, Liebfrauenstr. 34 None, 64289 Darmstadt
        240164: REWE Markt GmbH, Luisencenter 5 None, 64283 Darmstadt
        240657: REWE Markt GmbH, Dieburger Str. 24 None, 64287 Darmstadt
        240070: REWE Markt GmbH, Heinrichstr. 52 None, 64283 Darmstadt
        240269: REWE Markt GmbH, Schwarzer Weg 9 None, 64287 Darmstadt
        240225: REWE Markt GmbH, Rüdesheimer Str. 119-123 None, 64285 Darmstadt
        240801: REWE Markt GmbH, Flughafenstr. 7 None, 64347 Griesheim Darmstadt
        240795: REWE Markt GmbH, Schneppenhaeuser Str. 21 None, 64331 Weiterstadt / Gräfenhausen
        240277: REWE Michael Weisbrod oHG, Oberndorfer Straße 111 None, 64347 Griesheim
        240340: REWE Markt GmbH, Südliche Ringstr. 27 None, 64390 Erzhausen
        240126: REWE Markt GmbH, Heidelberger Landstr. 236-240 None, 64297 Darmstadt/Eberstadt
        240166: REWE Markt GmbH, Rheinstr. 47 None, 64367 Mühltal / Nieder-Ramstadt
        240276: REWE Markt GmbH, Eberstädter Str. 94 None, 64319 Pfungstadt
    """
    print("Checking REWE Angebote")
    market_id = 240070
    resp = requests.get(f"https://mobile-api.rewe.de/products/offer-search?categoryId=&marketId={market_id}", headers=headers)
    assert resp.status_code == 200
    j = resp.json()
    results_rewe = list()
    for item in j['items']:
        #print(item['name'])
        if "mate" in item['name'].lower():
            #print(f"REWE HIT\n{json.dumps(item, indent=4)}")
            results_rewe.append(item)
    return results_rewe


def send_mail(message):
    # credit: https://www.authsmtp.com/python/index.html

    msg = MIMEMultipart()
    msg['From'] = smtpfrom
    msg['To'] = smtpto
    msg['Subject'] = "Gibt's mal wieder Mate?"
    msg.attach(MIMEText(message, 'plain'))

    server = smtplib.SMTP_SSL(smtphost)
    server.login(username, password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    print("Sent mail")


if __name__ == '__main__':

    output = f"## Mate Checker Results {arrow.now().format()} ##\n\n"
    output += "###### BEGIN Tegut ######\n"
    output += f"Angebote der Woche: {get_tegut_angebot_url()}\n\n"
    output += do_tegut()
    output += "###### END Tegut ######\n\n\n"
    output += "###### BEGIN Rewe ######\n"
    rewe_list = do_rewe()
    for item in rewe_list:
        item_text = f"{item['name']} {item['price']} {item['_links']['image:m']['href']}\n"
        output += item_text
    output += "###### END Rewe ######"

    print(output)
    send_mail(output)

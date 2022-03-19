# Gibt es beim Rewe oder Tegut gerade Mate im Angebot?

Rewe hat eine API (ist aber leider gesperrt wenn man eine "Server-IP" hat). Für Tegut werden die Angebote mit pdgrep geparst.

### Install

```bash
apt install -y pdfgrep
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Example output
```bash
(venv) mate@banane:~/Ist-die-Mate-im-Angebot$ python mate-check.py 
Checking Tegut Angeote
Downloaded Tegut Angebote to tegut-angebote.pdf
    oder Rotwein aus Deutschland                                                     verschiedene Sorten,                                                oder stückige Tomaten,
                    Bio-Strauchcocktailtomaten                                                                                             Bio-Rucola
                                                    aus Italien oder Spanien,                             Tomate, 100 g = 1,06 €,                     Bio-Tahin Sesammus

Checking REWE Angebote
## Mate Checker Results 2022-03-16 11:04:04+01:00 ##

###### BEGIN Tegut ######
Angebote der Woche: https://static.tegut.com/fileadmin/tegut_upload/Dokumente/Aktuelle_Flugbl%C3%A4tter/tegut-prospekt-kw-11-2022-Hessen-Niedersachsen-Rheinland-Pfalz.pdf

    oder Rotwein aus Deutschland                                                     verschiedene Sorten,                                                oder stückige Tomaten,
                    Bio-Strauchcocktailtomaten                                                                                             Bio-Rucola
                                                    aus Italien oder Spanien,                             Tomate, 100 g = 1,06 €,                     Bio-Tahin Sesammus
###### END Tegut ######


###### BEGIN Rewe ######
Knorr Tomaten Ketchup 1.29 https://img.rewe-static.de/REWE11_2022/2360602/23631618-14_digital-image.png
Campo Verde Tomaten Polpa 2.29 https://img.rewe-static.de/REWE11_2022/2168054/31640841-9_digital-image.png
###### END Rewe ######
Sent mail
(venv) mate@banane:~/Ist-die-Mate-im-Angebot$ 
```

### Cronjob
chmod +x /home/mate/Ist-die-Mate-im-Angebot/mate-check.py
@daily /home/mate/Ist-die-Mate-im-Angebot/venv/bin/python /home/mate/Ist-die-Mate-im-Angebot/mate-check.py > /dev/null 2>&1


### TODO
- Ausgabe schön machen
- ToMATEn rausfiltern
- was wenn ne Exception kommt

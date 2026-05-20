# WOREN — who wore what?

Demo:
🔗 [woren](https://worensovellus.onrender.com)

Woren on asuinspiraatiosovellus asukriiseihin. Somessa tietoa on liikaa ja yleensä julkaisuilla yritetään myydä 
joko omaa henkilöbrändiä tai muun brändin tuotetta.
Tarkoituksena oli tehdä vilpitön ratkaisu tähän ongelmaan, tuoda people-watching käden ulottuvuudelle ja kannustamaan
muitakin kuin somevaikuttajia jakamaan asuja.

Idea on yksinkertainen: selaa muiden asuja, jaa omiasi. 

## Ominaisuudet

- Rekisteröityminen, kirjautuminen ja uloskirjautuminen
- Asujen lisääminen, muokkaaminen ja poistaminen
- Kuvat ja kuvaukset jokaiseen asuun
- Tykkäykset, kommentit ja repostaukset
- Haku tyylisuuntauksien ja kauden mukaan (minimalistic, fall/winter)
- Oma profiilisivu asuhistorialla ja statseillä

## Teknologiat
- Python 
- Flask
- SQLite
- HTML, CSS
- Docker
## Asennus
Asennus tapahtuu terminaalissa

- git clone https://github.com/leilapseudo/worensovellus

- cd worensovellus

- pip install flask

- sqlite3 database.db < schema.sql

- flask run

- Avaa selaimessa: http://127.0.0.1:5000

Jos sinulta löytyy Docker:

- git clone https://github.com/leilapseudo/worensovellus
- cd worensovellus
- docker compose up





# Ravintolat

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ravintola-arvosteluja.
* Käyttäjä näkee sovellukseen lisätyt ravintola-arvostelut.
* Käyttäjä pystyy etsimään ravintoloita hakusanalla.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ravintola-arvostelut.
* Käyttäjä pystyy valitsemaan ravintolalle yhden tai useamman luokittelun (esim. ravintolan kategoria, kaupunki, hintaluokka).
* Käyttäjä pystyy lisäämään ravintoloita suosikkeihin ja lisäämään arvostelun.
* Sovellus näyttää arvostelujen keskiarvot.

## Suuren tietomäärän testaus
Sovellusta testattu suurella tietomäärällä suorituskyvyn varmistukseksi.
Käytin datan generoimiseksi seed.py skriptiä, joka generoi tietokantaan 1000 ravintolaa yhdelle testikäyttäjälle, sekä loi 5000 kommenttia satunnaisesti eri ravintoloille.

Testauksen pohjalta toteutetut optimoinnit

Suuren datamäärän hallitsemiseksi sovelluksesta löytyy:
1. Sivutus
* Jotta kaikki ravintolat eivät lataudu yhdelle sivulle.
2. Tietokantaindeksit.
* Jotta hakeminen ja järjestäminen on nopeaa.

## Sovelluksen testaus

Asenna `flask`-kirjasto:

```
$ pip install flask werkzeug
```

Luo tietokannan taulut ja alustaa tietokannan:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < data.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```

# Ravintolat

* Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
* Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan ravintola-arvosteluja.
* Käyttäjä pystyy lisäämään kuvia ravintola-arvosteluun.
* Käyttäjä näkee sovellukseen lisätyt ravintola-arvostelut.
* Käyttäjä pystyy etsimään ravintoloita hakusanalla.
* Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät ravintola-arvostelut.
* Käyttäjä pystyy valitsemaan ravintolalle yhden tai useamman luokittelun (esim. ravintolan kategoria, kaupunki, hintaluokka).
* Käyttäjä pystyy lisäämään ravintoloita suosikkeihin ja tykkäämään muiden arvosteluista.

## Toteutuksen tilanne
Sovellus on kehitysvaiheessa. Seuraavat ominaisuudet on toteutettu:
- [x] Käyttäjän rekisteröityminen ja kirjautuminen (ja ohjaus etusivulle)
- [x] Ravintoloiden haku ja listaus
- [x] Ravintolan tietosivu ja kategorioiden näyttäminen
- [x] Ravintoloiden lisäys, muokkaus ja poisto

## Sovelluksen testaus

Asenna `flask`-kirjasto:

```
$ pip install flask
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

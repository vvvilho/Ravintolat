#Pylint-raportti

Pylint antaa seuraavan raportin.

```
************* Module app
app.py:1:0: C0114: Missing module docstring (missing-module-docstring)
app.py:14:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:19:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:37:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:43:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:71:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:71:0: R1710: Either all return statements in a function should return an expression, or none of them should. (inconsistent-return-statements)
app.py:100:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:125:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:131:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:159:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:205:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:222:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:284:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:307:0: C0116: Missing function or method docstring (missing-function-docstring)
app.py:327:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module models
models.py:1:0: C0114: Missing module docstring (missing-module-docstring)
models.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:10:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:15:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:32:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:32:0: R0913: Too many arguments (6/5) (too-many-arguments)
models.py:32:0: R0917: Too many positional arguments (6/5) (too-many-positional-arguments)
models.py:45:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:55:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:65:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:69:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:73:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:77:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:82:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:92:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:102:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:102:0: R0913: Too many arguments (6/5) (too-many-arguments)
models.py:102:0: R0917: Too many positional arguments (6/5) (too-many-positional-arguments)
models.py:110:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:114:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:118:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:127:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:131:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:135:4: R1705: Unnecessary "else" after "return", remove the "else" and de-indent the code inside it (no-else-return)
models.py:145:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:155:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:160:0: C0116: Missing function or method docstring (missing-function-docstring)
models.py:170:0: C0116: Missing function or method docstring (missing-function-docstring)
************* Module db
db.py:1:0: C0114: Missing module docstring (missing-module-docstring)
db.py:4:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:10:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:10:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
db.py:17:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:20:0: C0116: Missing function or method docstring (missing-function-docstring)
db.py:20:0: W0102: Dangerous default value [] as argument (dangerous-default-value)
************* Module config
config.py:1:0: C0114: Missing module docstring (missing-module-docstring)
config.py:1:0: C0103: Constant name "secret_key" doesn't conform to UPPER_CASE naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 8.27/10 (previous run: 8.18/10, +0.10)
```

Käydään läpi raportti ja perustellaan miksi mainittuja asioita ei ole korjattu.

## Docstring-ilmoitukset

Suurin osa ilmoituksista liittyy puuttuviin docstringeihin. Sovellusta tehdessä docstingit jätetty tarkoituksella pois, sillä kurssin materiaalissakaan ei käytetty.

## Epäjohdonmukaiset palautuslauseet

Koska funktiossa on käytössä kaksi if-lausetta metodeille GET ja POST pylint olettaa, että voisi tulla tilanne, jossa metodi olisi jokin muu. Kyseisessä sovelluksessa tämä ei kuitenkaan ole mahdollista.

## Liian monta argumenttia

Pylint noudattaa sääntöä, jonka mukaan funktiolla saa olla korkeintaan 5 argumenttiä. Mutta sovelluksessa ravintolan luominen vaatii 6 argumenttiä, jotta tietokantaan saa täytettyä oikeat tiedot. Kaikki argumentit siis ovat olennaisia.

## Tarpeeton else

Koodi olisi mahdollista ilman ylimääräistä else -haaraa, mutta else on jätetty koodiin koska se tekee koodista selkeämmän ja helpommin luettavan.

## Vaarallinen oletusarvo

Ilmoitus liittyy seuraavaan funktioon:

```
def execute(sql, params=[]):
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid
    con.close()
```

Ongelmana on, että periaatteessa tyhjään listaan voisi viitata, jossain muuaalla koodissa, joka muuttaisi sitä. Kuitenkaan se ei ole ongelma, sillä listaoliota ei muuteta koodissa.

## Vakion nimi

```
config.py:1:0: C0103: Constant name "secret_key" doesn't conform to UPPER_CASE naming style (invalid-name)
```

Pylint tulkitsee muuttujan vakioksi. Näyttää koodissa, kuitenkin tyyllikkäämmältä, kun muuttuja on kirjoitettu pienellä





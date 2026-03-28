

import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if result and check_password_hash(result[0]["password_hash"], password):
            session["user_id"] = result[0]["id"]
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/restaurants/create", methods=["GET", "POST"])
def restaurants_create():

    user_id = session.get("user_id")
    if not user_id:
        return "Sinun täytyy kirjautua sisään lisätäksesi ravintolan"


    cities = db.query("SELECT id, name FROM cities ORDER BY name")
    categories = db.query("SELECT id, name FROM categories ORDER BY name")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        city_id = request.form.get("city_id")  
        address = request.form.get("address", "").strip()
        price_level = request.form.get("price_level") or None

        if not name:
            flash("Name is required.")
            return render_template("create.html", cities=cities, categories=categories, form=request.form)

        db.execute("""
            INSERT INTO restaurants (name, description, city_id, price_level, address, created_by)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            name,
            description,
            int(city_id) if city_id and city_id.isdigit() else None,
            int(price_level) if price_level and price_level.isdigit() else None,
            address,
            session.get("user_id") 
        ])

  
        rid = db.last_insert_id()


        for cid in request.form.getlist("categories"):
            if cid.isdigit():
                db.execute(
                    "INSERT INTO restaurant_categories (restaurant_id, category_id) VALUES (?, ?)",
                    [rid, int(cid)]
                )


        flash(f"Ravintola {name} tallennettu!")
        return redirect("/")
    return render_template("create.html", cities=cities, categories=categories)
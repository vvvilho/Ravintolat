import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
from functools import wraps

app = Flask(__name__)
app.secret_key = config.secret_key


@app.route("/")
def index():
    sql = """
    SELECT r.id, r.name, r.price_level, r.created_by, c.name AS city_name 
    FROM restaurants r
    LEFT JOIN cities c ON r.city_id = c.id
    ORDER BY r.name;
    """
    restaurants = db.query(sql)
    return render_template("index.html", restaurants=restaurants)

@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    sql_res = """
            SELECT r.*, c.name AS city_name, u.username AS creator_name
            FROM restaurants r
            LEFT JOIN cities c ON r.city_id = c.id
            LEFT JOIN users u ON r.created_by = u.id
            WHERE r.id = ?;
        """
    res = db.query(sql_res, [restaurant_id])

    if not res:
        return "Ravintolaa ei löytynyt", 404

    restaurant = res[0]

    sql_cats = """
        SELECT c.name 
        FROM categories c
        JOIN restaurant_categories rc ON c.id = rc.category_id
        WHERE rc.restaurant_id = ?;
    """
    categories = db.query(sql_cats, [restaurant_id])

    return render_template("restaurant.html", restaurant=restaurant, categories=categories)



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
    session.clear()
    flash("Uloskirjautuminen onnistui.")
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

@app.route("/restaurants/edit/<int:restaurant_id>", methods=["GET", "POST"])
def edit_restaurant(restaurant_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Kirjaudu sisään muokataksesi.")
        return redirect("/login")

    res = db.query("SELECT * FROM restaurants WHERE id = ?", [restaurant_id])
    if not res:
        return "Ravintolaa ei löytynyt", 404
    restaurant = res[0]

    if restaurant["created_by"] != user_id:
        flash("Voit muokata vain omia ilmoituksiasi.")
        return redirect("/")

    cities = db.query("SELECT id, name FROM cities ORDER BY name")
    categories = db.query("SELECT id, name FROM categories ORDER BY name")
    
    current_cats = db.query("SELECT category_id FROM restaurant_categories WHERE restaurant_id = ?", [restaurant_id])
    current_cat_ids = [c["category_id"] for c in current_cats]

    if request.method == "POST":
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        city_id = request.form.get("city_id")
        address = request.form.get("address", "").strip()
        price_level = request.form.get("price_level")
        
        if not name:
            flash("Nimi on pakollinen.")
            return render_template("edit.html", restaurant=restaurant, cities=cities, categories=categories, current_cat_ids=current_cat_ids)

        db.execute("""
            UPDATE restaurants 
            SET name = ?, description = ?, city_id = ?, price_level = ?, address = ?
            WHERE id = ?
        """, [
            name, description, 
            int(city_id) if city_id else None, 
            int(price_level) if price_level else None, 
            address, restaurant_id
        ])

        db.execute("DELETE FROM restaurant_categories WHERE restaurant_id = ?", [restaurant_id])
        for cid in request.form.getlist("categories"):
            if cid.isdigit():
                db.execute("INSERT INTO restaurant_categories (restaurant_id, category_id) VALUES (?, ?)", [restaurant_id, int(cid)])

        flash("Ilmoitus päivitetty onnistuneesti!")
        return redirect("/") 

    return render_template("edit.html", restaurant=restaurant, cities=cities, categories=categories, current_cat_ids=current_cat_ids)


@app.route("/restaurants/delete/<int:restaurant_id>", methods=["POST"])
def delete_restaurant(restaurant_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Kirjaudu sisään poistaaksesi.")
        return redirect("/login")

    res = db.query("SELECT created_by FROM restaurants WHERE id = ?", [restaurant_id])
    if not res:
        return "Ravintolaa ei löytynyt", 404
    
    if res[0]["created_by"] != user_id:
        flash("Voit poistaa vain omia ilmoituksiasi.")
        return redirect("/")

    db.execute("DELETE FROM restaurants WHERE id = ?", [restaurant_id])
    
    flash("Ravintola poistettu onnistuneesti.")
    return redirect("/")
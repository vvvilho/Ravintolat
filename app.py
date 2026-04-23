import sqlite3
from functools import wraps
import secrets

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash


import db
import config


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

@app.route("/find_restaurants")
def find_restaurants():
    query = request.args.get("query", "").strip()
    params = []
    sql = """
        SELECT r.id, r.name, r.description, r.created_by
        FROM restaurants r
    """
    where = []
    if query:
        where.append("(r.name LIKE ? OR r.description LIKE ?)")
        like = f"%{query}%"
        params.extend([like, like])

    if where:
        sql += " WHERE " + " AND ".join(where)

    sql += " ORDER BY r.name COLLATE NOCASE"

    rows = db.query(sql, params)
    return render_template("restaurants_list.html", items=rows, query=query)


@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    sql_res = """
            SELECT r.*, c.name AS city_name, u.username AS creator_name, u.id AS creator_id
            FROM restaurants r
            LEFT JOIN cities c ON r.city_id = c.id
            LEFT JOIN users u ON r.created_by = u.id
            WHERE r.id = ?;
        """
    res = db.query(sql_res, [restaurant_id])

    if not res:
        return "Ravintolaa ei löytynyt", 404
    
    comments = db.query("""
        SELECT c.content, c.stars, c.created_at, u.username 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.restaurant_id = ? 
        ORDER BY c.created_at DESC
    """, [restaurant_id])

    average_stars = 0
    if comments:
        total_stars = sum(c["stars"] for c in comments if c["stars"])
        average_stars = round(total_stars / len(comments), 1)
    is_favorite = False    
    if session.get("user_id"):
        fav = db.query("SELECT 1 FROM favorites WHERE user_id = ? AND restaurant_id = ?", 
                       [session["user_id"], restaurant_id])  
        if fav:
            is_favorite = True

    restaurant = res[0]

    sql_cats = """
        SELECT c.name 
        FROM categories c
        JOIN restaurant_categories rc ON c.id = rc.category_id
        WHERE rc.restaurant_id = ?;
    """
    categories = db.query(sql_cats, [restaurant_id])

    return render_template("restaurant.html", restaurant=restaurant, categories=categories, comments=comments, is_favorite=is_favorite, average_stars=average_stars)



@app.route("/register") 
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    if request.method == "POST":
        check_csrf()
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
        flash("Tunnus on jo varattu")
        return render_template("register.html")

    flash("Tunnus luotu")
    return redirect("/")

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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("Väärä tunnus tai salasana.")
            return render_template("login.html")

from flask import abort 

def check_csrf():
    if session.get("csrf_token") != request.form.get("csrf_token"):
        abort(403)

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
        check_csrf()
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
    
    if request.method == "POST":
        check_csrf()

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
        flash("Sinun täytyy kirjautua sisään poistaaksesi")
        return redirect("/login")
    check_csrf()
    res = db.query("SELECT created_by FROM restaurants WHERE id = ?", [restaurant_id])
    if not res:
        return "Ravintolaa ei löytynyt", 404
    
    if res[0]["created_by"] != user_id:
        flash("Voit poistaa vain omia iloituksiasi.")
        return redirect("/")
    
    db.execute("DELETE FROM restaurants WHERE id = ?", [restaurant_id])
    
    flash("Ravintola poistettu onnistuneesti.")
    return redirect("/")

@app.route("/user/<int:user_id>")
def user_page(user_id):
    user_info = db.query("SELECT username FROM users WHERE id = ?", [user_id])
    if not user_info:
        return "Käyttäää ei löydy", 404
    

    sql_own = "SELECT id, name FROM restaurants WHERE created_by = ? ORDER BY name"
    own_restaurants = db.query(sql_own, [user_id])

    sql_favs = """
        SELECT r.id, r.name 
        FROM restaurants r
        JOIN favorites f ON r.id = f.restaurant_id
        WHERE f.user_id = ?
        ORDER BY r.name
    """
    favorite_restaurants = db.query(sql_favs, [user_id])

    return render_template("user_page.html",
                           username=user_info[0]["username"],
                           restaurants=own_restaurants,
                           favorites=favorite_restaurants,
                           count=len(own_restaurants))

@app.route("/restaurant/<int:id>/favorite", methods=["POST"])
def toggle_favorite(id):
    check_csrf()
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    existing = db.query("SELECT 1 FROM favorites WHERE user_id = ? AND restaurant_id = ?", [user_id, id])
    if existing:
        db.execute("DELETE FROM favorites WHERE user_id = ? AND restaurant_id = ?", [user_id, id])
        flash("Poistettu suosikeista.")
    else:
        db.execute("INSERT INTO favorites (user_id, restaurant_id) VALUES (?, ?)", [user_id, id])
        flash("Lisätty suosikkeihin!")
        
    return redirect(f"/restaurant/{id}")

@app.route("/restaurant/<int:id>/comment", methods=["POST"])
def add_comment(id):
    check_csrf()
    user_id = session.get("user_id")
    if not user_id:
        flash("Kirjaudu sisään arvostellaksesi.")
        return redirect("/login")

    content = request.form.get("content", "").strip()
    stars = request.form.get("stars")

    if not content:
        flash("Arvostelu ei voi olla tyhjä.")
        return redirect(f"/restaurant/{id}")

    db.execute("""
        INSERT INTO comments (restaurant_id, user_id, content, stars) 
        VALUES (?, ?, ?, ?)
    """, [id, user_id, content, int(stars) if stars else 5])

    flash("Arvostelu lisätty!")
    return redirect(f"/restaurant/{id}")
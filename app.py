from flask import Flask, redirect, render_template, request, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import config
import models
import db
import sqlite3

app = Flask(__name__)
app.secret_key = config.secret_key

def check_csrf():
    if session.get("csrf_token") != request.form.get("csrf_token"):
        abort(403)

@app.route("/")
def index():
    restaurants = models.get_restaurants()
    return render_template("index.html", restaurants=restaurants)

@app.route("/find_restaurants")
def find_restaurants():
    query = request.args.get("query", "").strip()
    items = models.find_restaurants(query)
    return render_template("restaurants_list.html", items=items, query=query)

@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    restaurant = models.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return "Ravintolaa ei löytynyt", 404

    comments = models.get_comments_by_restaurant_id(restaurant_id)
    average_stars = 0
    if comments:
        total_stars = sum(c["stars"] for c in comments if c["stars"])
        average_stars = round(total_stars / len(comments), 1)

    is_favorite = False
    if session.get("user_id"):
        fav = models.is_favorite(session["user_id"], restaurant_id)
        is_favorite = bool(fav)

    categories = models.get_restaurant_categories(restaurant_id)

    return render_template(
        "restaurant.html",
        restaurant=restaurant[0],
        comments=comments,
        average_stars=average_stars,
        is_favorite=is_favorite,
        categories=categories
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return render_template("register.html")
    
    if request.method == "POST":
        check_csrf()
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        
        if password1 != password2:
            flash("VIRHE: Salasanat eivät ole samat.")
            return render_template("register.html")
        
        password_hash = generate_password_hash(password1)
        
        try:
            db.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", [username, password_hash])
        except sqlite3.IntegrityError:
            flash("Tunnus on jo varattu.")
            return render_template("register.html")
        
        flash("Tunnus luotu onnistuneesti!")
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(16)
        return render_template("login.html")

    if request.method == "POST":
        check_csrf()
        
        username = request.form["username"]
        password = request.form["password"]
        
        user = db.query("SELECT id, password_hash FROM users WHERE username = ?", [username])
        
        if user and check_password_hash(user[0]["password_hash"], password):
            session["user_id"] = user[0]["id"]
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
            
        flash("Väärä tunnus tai salasana")
        
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Uloskirjautuminen onnistui.")
    return redirect("/")

@app.route("/user/<int:user_id>")
def user_page(user_id):
    user_info = models.get_user_info(user_id)
    if not user_info:
        return "Käyttäjää ei löydy", 404

    own_restaurants = models.get_user_restaurants(user_id)
    favorite_restaurants = models.get_user_favorites(user_id)

    return render_template("user_page.html",
                           username=user_info[0]["username"],
                           restaurants=own_restaurants,
                           favorites=favorite_restaurants,
                           count=len(own_restaurants))

@app.route("/restaurants/create", methods=["GET", "POST"])
def restaurants_create():
    user_id = session.get("user_id")
    if not user_id:
        flash("Sinun täytyy kirjautua sisään lisätäksesi ravintolan.")
        return redirect("/login")

    cities = models.get_cities()
    categories = models.get_categories()

    if request.method == "POST":
        check_csrf()
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        city_id = request.form.get("city_id")
        address = request.form.get("address", "").strip()
        price_level = request.form.get("price_level")

        if not name:
            flash("Nimi on pakollinen.")
            return render_template("create.html", cities=cities, categories=categories)

        c_id = int(city_id) if city_id and city_id.isdigit() else None
        p_lvl = int(price_level) if price_level and price_level.isdigit() else None


        new_restaurant_id = models.create_restaurant(name, description, c_id, p_lvl, address, user_id)


        selected_categories = request.form.getlist("categories")
        for cid in selected_categories:
            if cid.isdigit():
                models.add_restaurant_category(new_restaurant_id, int(cid))

        flash(f"Ravintola {name} tallennettu!")
        return redirect("/")
        
    return render_template("create.html", cities=cities, categories=categories)


@app.route("/restaurant/<int:id>/favorite", methods=["POST"])
def toggle_favorite(id):
    check_csrf()
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    
    existing = models.is_favorite(user_id, id)
    if existing:
        db.execute("DELETE FROM favorites WHERE user_id = ? AND restaurant_id = ?", [user_id, id])
        flash("Poistettu suosikeista.")
    else:
        db.execute("INSERT INTO favorites (user_id, restaurant_id) VALUES (?, ?)", [user_id, id])
        flash("Lisätty suosikkeihin!")
        
    return redirect(f"/restaurant/{id}")

@app.route("/restaurants/edit/<int:restaurant_id>", methods=["GET", "POST"])
def edit_restaurant(restaurant_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Kirjaudu sisään muokataksesi.")
        return redirect("/login")

    restaurant = models.get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return "Ravintolaa ei löytynyt", 404

    if restaurant[0]["created_by"] != user_id:
        flash("Voit muokata vain omia ilmoituksiasi.")
        return redirect("/")
    
    cities = models.get_cities()
    categories = models.get_categories()
    current_cats = models.get_restaurant_categories(restaurant_id)
    current_cat_ids = [c["category_id"] for c in current_cats]

    if request.method == "POST":
        check_csrf()
        name = request.form["name"].strip()
        description = request.form.get("description", "").strip()
        city_id = request.form.get("city_id")
        address = request.form.get("address", "").strip()
        price_level = request.form.get("price_level")
        
        if not name:
            flash("Nimi on pakollinen.")
            return render_template("edit.html", restaurant=restaurant[0], cities=cities, categories=categories, current_cat_ids=current_cat_ids)

        models.update_restaurant(
            restaurant_id, 
            name, 
            description, 
            int(city_id) if city_id else None, 
            int(price_level) if price_level else None, 
            address
        )

        models.delete_restaurant_categories(restaurant_id)
        for cid in request.form.getlist("categories"):
            if cid.isdigit():
                models.add_restaurant_category(restaurant_id, int(cid))

        flash("Ilmoitus päivitetty onnistuneesti!")
        return redirect("/") 

    return render_template("edit.html", restaurant=restaurant[0], cities=cities, categories=categories, current_cat_ids=current_cat_ids)


@app.route("/restaurants/delete/<int:restaurant_id>", methods=["POST"])
def delete_restaurant(restaurant_id):
    user_id = session.get("user_id")
    if not user_id:
        flash("Sinun täytyy kirjautua sisään poistaaksesi ravintolan.")
        return redirect("/login")
        
    check_csrf()

    res_list = models.get_restaurant_by_id(restaurant_id)
    if not res_list:
        return "Ravintolaa ei löytynyt", 404
        
    restaurant = res_list[0]

    if restaurant["created_by"] != user_id:
        flash("Voit poistaa vain omia ilmoituksiasi.")
        return redirect("/")

    models.delete_restaurant(restaurant_id)
    
    flash(f"Ravintola {restaurant['name']} ja siihen liittyvät tiedot poistettu.")
    return redirect("/")

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

    models.add_comment(id, user_id, content, int(stars) if stars else 5)

    flash("Arvostelu lisätty!")
    return redirect(f"/restaurant/{id}")

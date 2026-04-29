import db
from db import execute

def create_user(username, password_hash):
    execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        [username, password_hash]
    )

def get_user_by_username(username):
    sql = """SELECT id, password_hash FROM users WHERE username = ?"""
    return db.query(sql, [username])


def get_restaurants():
    sql = """
    SELECT r.id, r.name, r.price_level, r.created_by, c.name AS city_name 
    FROM restaurants r
    LEFT JOIN cities c ON r.city_id = c.id
    ORDER BY r.name;
    """
    return db.query(sql)

def find_restaurants(query):
    sql = """
        SELECT r.id, r.name, r.description, r.price_level, c.name AS city_name
        FROM restaurants r
        LEFT JOIN cities c ON r.city_id = c.id
    """
    params = []
    if query:
        where = "(r.name LIKE ? OR r.description LIKE ?)"
        sql += f" WHERE {where}"
        like = f"%{query}%"
        params.extend([like, like])

    sql += " ORDER BY r.name COLLATE NOCASE"
    return db.query(sql, params)


def create_restaurant(name, description, city_id, price_level, address, user_id):
    sql = """
        INSERT INTO restaurants (name, description, city_id, price_level, address, created_by)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    db.execute(sql, [name, description, city_id, price_level, address, user_id])
    res = db.query("""
        SELECT id FROM restaurants 
        WHERE name = ? AND created_by = ? 
        ORDER BY id DESC LIMIT 1
    """, [name, user_id])
    return res[0]["id"] if res else None

def get_restaurant_by_id(restaurant_id):
    sql = """
        SELECT r.*, c.name AS city_name, u.username AS creator_name, u.id AS creator_id
        FROM restaurants r
        LEFT JOIN cities c ON r.city_id = c.id
        LEFT JOIN users u ON r.created_by = u.id
        WHERE r.id = ?;
    """
    return db.query(sql, [restaurant_id])

def get_comments_by_restaurant_id(restaurant_id):
    sql = """
        SELECT c.content, c.stars, c.created_at, u.username 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.restaurant_id = ? 
        ORDER BY c.created_at DESC
    """
    return db.query(sql, [restaurant_id])

def get_cities():
    sql = "SELECT id, name FROM cities ORDER BY name"
    return db.query(sql)

def get_categories():
    sql = "SELECT id, name FROM categories ORDER BY name"
    return db.query(sql)

def is_favorite(user_id, restaurant_id):
    sql = "SELECT 1 FROM favorites WHERE user_id = ? AND restaurant_id = ?"
    return db.query(sql, [user_id, restaurant_id])

def get_user_info(user_id):
    sql = "SELECT username FROM users WHERE id = ?"
    return db.query(sql, [user_id])

def get_user_restaurants(user_id):
    sql = "SELECT id, name FROM restaurants WHERE created_by = ? ORDER BY name"
    return db.query(sql, [user_id])

def get_user_favorites(user_id):
    sql = """
        SELECT r.id, r.name 
        FROM restaurants r
        JOIN favorites f ON r.id = f.restaurant_id
        WHERE f.user_id = ?
        ORDER BY r.name
    """
    return db.query(sql, [user_id])

def get_restaurant_categories(restaurant_id):
    sql = """
        SELECT c.id AS category_id, c.name 
        FROM categories c
        JOIN restaurant_categories rc ON c.id = rc.category_id
        WHERE rc.restaurant_id = ?;
    """
    return db.query(sql, [restaurant_id])


def update_restaurant(restaurant_id, name, description, city_id, price_level, address):
    sql = """
        UPDATE restaurants 
        SET name = ?, description = ?, city_id = ?, price_level = ?, address = ?
        WHERE id = ?
    """
    db.execute(sql, [name, description, city_id, price_level, address, restaurant_id])

def delete_restaurant_categories(restaurant_id):
    sql = "DELETE FROM restaurant_categories WHERE restaurant_id = ?"
    db.execute(sql, [restaurant_id])

def add_restaurant_category(restaurant_id, category_id):
    sql = "INSERT INTO restaurant_categories (restaurant_id, category_id) VALUES (?, ?)"
    db.execute(sql, [restaurant_id, category_id])

def add_comment(restaurant_id, user_id, content, stars):
    stars = max(1, min(5, int(stars)))
    sql = """
        INSERT INTO comments (restaurant_id, user_id, content, stars) 
        VALUES (?, ?, ?, ?)
    """
    db.execute(sql, [restaurant_id, user_id, content, stars])


def delete_restaurant(restaurant_id):
    sql = "DELETE FROM restaurants WHERE id = ?"
    db.execute(sql, [restaurant_id])

def toggle_favorite(user_id, restaurant_id):
    sql_check = "SELECT 1 FROM favorites WHERE user_id = ? AND restaurant_id = ?"
    existing = db.query(sql_check, [user_id, restaurant_id])

    if existing:
        sql_delete = "DELETE FROM favorites WHERE user_id = ? AND restaurant_id = ?"
        db.execute(sql_delete, [user_id, restaurant_id])
        return False
    else:
        sql_insert = "INSERT INTO favorites (user_id, restaurant_id) VALUES (?, ?)"
        db.execute(sql_insert, [user_id, restaurant_id])
        return True

INSERT INTO cities (name) VALUES ('Helsinki'), ('Tampere'), ('Turku'), ('Oulu');
INSERT INTO categories (name) VALUES ('Pizzeria'), ('Sushi'), ('Burgers'), ('Fine Dining'), ('Vegan'), ('Thai'),
("Lounas"), ("Kahvila"), ("Italialainen"), ("Meksikolainen");

INSERT INTO restaurant_categories (restaurant_id, category_id) 
VALUES (1, 1), (2, 2), (3, 1);
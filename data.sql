INSERT INTO cities (name) VALUES ('Helsinki'), ('Tampere'), ('Turku'), ('Oulu');
INSERT INTO categories (name) VALUES ('Pizzeria'), ('Sushi'), ('Burgers'), ('Fine Dining'), ('Vegan'), ('Thai');

INSERT INTO restaurants (name, description, address, city_id, price_level, created_by) 
VALUES 
('Pekan pizza', 'Hyvät pitsat ja mukava tunnelma!', 'Katu 23', 1, 2, 1),
('Sushi ravintola soija', 'Tuoretta sushia ja rauhallinen tunnelma.', 'Tie 5', 1, 3, 1),
('Jukan Burger', 'Isot annokset.', 'Kuja 8', 2, 2, 1);


INSERT INTO restaurant_categories (restaurant_id, category_id) 
VALUES (1, 1), (2, 2), (3, 1);
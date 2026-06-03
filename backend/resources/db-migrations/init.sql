CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    price DOUBLE NOT NULL,
    stock INT NOT NULL
);

CREATE TABLE IF NOT EXISTS favorite_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    item_id INT NOT NULL,
    UNIQUE(user_id, item_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (item_id) REFERENCES items(id)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    shipping_address VARCHAR(500) NOT NULL,
    total_price DOUBLE NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    item_id INT NOT NULL,
    quantity INT NOT NULL,
    price_per_item DOUBLE NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(order_id, item_id)
);

INSERT IGNORE INTO items (name, price, stock)
VALUES
    ('Argentina Jersey', 95, 18),
    ('Brazil Jersey', 92, 12),
    ('France Jersey', 94, 15),
    ('England Jersey', 90, 20),
    ('Spain Jersey', 88, 19),
    ('Germany Jersey', 89, 17),
    ('Portugal Jersey', 91, 11),
    ('Italy Jersey', 90, 16),
    ('Netherlands Jersey', 87, 14),
    ('Belgium Jersey', 82, 10),
    ('Croatia Jersey', 84, 9),
    ('Uruguay Jersey', 83, 8),
    ('Colombia Jersey', 80, 7),
    ('Mexico Jersey', 81, 13),
    ('Japan Jersey', 79, 22),
    ('Morocco Jersey', 82, 11),
    ('USA Jersey', 78, 24),
    ('Switzerland Jersey', 74, 6),
    ('Sweden Jersey', 73, 5),
    ('Norway Jersey', 75, 7),
    ('Turkey Jersey', 72, 6),
    ('Austria Jersey', 71, 5),
    ('Denmark Jersey', 74, 6),
    ('Poland Jersey', 73, 5),
    ('Serbia Jersey', 70, 4),
    ('Australia Jersey', 69, 5),
    ('Canada Jersey', 68, 8),
    ('South Korea Jersey', 70, 10),
    ('Nigeria Jersey', 67, 4),
    ('Cameroon Jersey', 65, 3),
    ('Senegal Jersey', 69, 5),
    ('Ivory Coast Jersey', 68, 4),
    ('Ecuador Jersey', 66, 4),
    ('Paraguay Jersey', 65, 3),
    ('Chile Jersey', 72, 5),
    ('Saudi Arabia Jersey', 60, 2),
    ('Israel Jersey', 120, 200);


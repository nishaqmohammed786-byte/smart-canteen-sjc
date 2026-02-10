-- schema.sql
CREATE DATABASE IF NOT EXISTS smart_canteen;
USE smart_canteen;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    menu_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(menu_id) REFERENCES menu(id)
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(50),
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

-- seed.sql
INSERT INTO menu (name, price) VALUES ('Burger', 599), ('Pizza', 899), ('Fries', 299);
INSERT INTO users (email, password) VALUES ('admin@canteen.com', 'admin@123'); -- hashed password

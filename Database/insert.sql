-- Inserting example data into the products table
INSERT INTO products (product_id, url, product_code, product_name) OVERRIDING SYSTEM VALUE VALUES
(1, 'http://example.com/product1', 'P001', 'Product 1'),
(2, 'http://example.com/product2', 'P002', 'Product 2'),
(3, 'http://example.com/product3', 'P003', 'Product 3'),
(4, 'http://example.com/product4', 'P004', 'Product 4'),
(5, 'http://example.com/product5', 'P005', 'Product 5'),
(6, 'http://example.com/product6', 'P006', 'Product 6');

-- Inserting example data into the users table
INSERT INTO users (user_id, email) OVERRIDING SYSTEM VALUE VALUES
(1, 'user1@example.com'),
(2, 'user2@example.com'),
(3, 'user3@example.com');

-- Inserting example data into the subscriptions table
INSERT INTO subscriptions (user_id, product_id, price_threshold) VALUES
(1, 1, 20.00),
(2, 2, 25.00),
(3, 3, 30.00);

-- Inserting example data into the price_readings table
INSERT INTO price_readings (product_id, reading_at, price) VALUES
(1, '2024-06-19 10:00:00', 19.99),
(2, '2024-06-19 11:00:00', 24.99),
(4, '2024-06-19 12:02:00', 228.99);
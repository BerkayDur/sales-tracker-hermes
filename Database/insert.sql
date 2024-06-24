-- Inserting example data into the websites table
INSERT INTO websites (website_name) VALUES
('www.asos.com'),
('store.steampowered.com');

-- Inserting example data into the products table
INSERT INTO products (url, product_code, product_name, website_id) VALUES
('https://www.asos.com/adidas-performance/adidas-running-response-trainers-in-white-and-blue/prd/203474246#colourWayId-203474304', '203474246', 'adidas Running Response trainers in white and blue', 1),
('https://www.asos.com/new-balance/new-balance-hierro-mid-trail-running-trainers-in-black/prd/202421541#colourWayId-202421546', '202421541', 'New Balance Hierro Mid trail running trainers in black', 1);

-- Inserting example data into the users table
INSERT INTO users (email) VALUES
('trainee.berkay.dur@sigmalabs.co.uk'),
('trainee.daniel.hudson@sigmalabs.co.uk');

-- Inserting example data into the subscriptions table
INSERT INTO subscriptions (user_id, product_id, price_threshold) VALUES
(1, 1, 20.00),
(2, 2, 25.00),
(1, 2, 30.00);

-- Inserting example data into the price_readings table
INSERT INTO price_readings (product_id, reading_at, price) VALUES
(1, '2024-06-19 10:00:00', 300.00),
(2, '2024-06-19 11:00:00', 20.00);
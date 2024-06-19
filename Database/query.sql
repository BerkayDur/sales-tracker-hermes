-- File to query the database



-- Example queries for each table
SELECT * FROM price_readings;

SELECT * FROM products;

SELECT * FROM subscriptions;

SELECT * FROM users;

-- A query across all of the tables
SELECT * FROM products 
JOIN price_readings USING (product_id) 
JOIN subscriptions USING (product_id) 
JOIN users USING (user_id);
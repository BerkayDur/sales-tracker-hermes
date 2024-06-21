-- File to query the database

-- Example queries for each table
SELECT * FROM users;
SELECT * FROM products;
SELECT * FROM subscriptions;
SELECT * FROM price_readings;

-- A query across all of the tables
SELECT * FROM products
FULL OUTER JOIN price_readings USING (product_id)
FULL OUTER JOIN subscriptions USING (product_id)
FULL OUTER JOIN users USING (user_id);
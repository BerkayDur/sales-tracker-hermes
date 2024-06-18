DROP TABLE IF EXISTS price_readings, subscriptions, users, products;

CREATE TABLE products(
    product_id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL,
    CONSTRAINT product_url_unique UNIQUE (url)
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    CONSTRAINT user_email_unique UNIQUE (email)
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    price_threshold DECIMAL(10, 2)
);

CREATE TABLE price_readings (
    reading_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    timestamp TIMESTAMP(0) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
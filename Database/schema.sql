DROP TABLE IF EXISTS price_readings, subscriptions, users, products;


CREATE TABLE products(
    product_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    product_code TEXT NOT NULL,
    product_name TEXT NOT NULL
);

CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE subscriptions (
    subscription_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users (user_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    price_threshold DECIMAL(12, 2)
);

CREATE TABLE price_readings (
    reading_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    reading_at TIMESTAMP(0) NOT NULL,
    price DECIMAL(12, 2) NOT NULL
);
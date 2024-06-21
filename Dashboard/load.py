"""Load Script: Populates the product table with the product information"""
from os import _Environ, environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from extract import extract_product_information


def configure_logging():
    """Sets up basic logger."""
    return logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_connection(config: _Environ) -> connection:
    """Establishes a connection with the database."""
    return psycopg2.connect(
        user=config["DB_USER"],
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        # password=config["DB_PASSWORD"],
        # port=config["DB_PORT"]
    )


def get_cursor(conn: connection) -> cursor:
    """Returns a cursor for the database."""
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def insert_product_information_database(conn: connection, extracted_data):
    "Inserts product name and code into the database."
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    logging.info("Inserting product data into the database")
    with get_cursor(conn) as cur:
        cur.execute(
            """INSERT INTO PRODUCTS (url, product_code, product_name) VALUES (%s, %s, %s)""",
            extracted_data)
        conn.commit()
    logging.info("Product information successfully added into the database")


def load_product_data():
    """Retrieves product information, inserts it into a database."""

    configure_logging()
    conn = get_connection(ENV)
    extracted_data = extract_product_information()
    insert_product_information_database(conn, extracted_data)


if __name__ == '__main__':
    load_dotenv()

    load_product_data()

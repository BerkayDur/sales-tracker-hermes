"""Load Script: Populates the product table with the product information"""
from os import _Environ, environ
import logging

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection
from extract_combined import extract_product_information
from helpers import get_connection, get_cursor


def insert_product_information(conn: connection, extracted_data: tuple):
    "Inserts product name and code into the database."
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    if not isinstance(extracted_data, tuple) or len(extracted_data) != 3:
        raise TypeError('Extracted data must be a tuple or length 3.')

    if not all(isinstance(detail, str) for detail in extracted_data):
        raise TypeError('All elements of the extracted data must be strings.')

    logging.info("Inserting product data into the database")
    with get_cursor(conn) as cur:
        cur.execute(
            """INSERT INTO PRODUCTS (url, product_code, product_name) VALUES (%s, %s, %s)""",
            extracted_data)
        conn.commit()
    logging.info("Product information successfully added into the database")


def load_product_data(config: _Environ, product_url: str) -> None:
    """Retrieves product information and inserts it into the database."""
    logging.info("Trying to load product information")
    conn = get_connection(config)
    extracted_data = extract_product_information(product_url)

    if not extracted_data:
        raise ValueError('Extraction Failed.')
    try:
        insert_product_information(conn, extracted_data)
        logging.info("Loading successfully completed!")
    except (TypeError, psycopg2.Error) as e:
        logging.error("Unable to load data %s", e)


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    load_dotenv()
    load_product_data(environ, 'https://www.asos.com/asos-design/asos-design-disney-oversized-unisex-tee-in-off-white-with-mickey-mouse-graphic-prints/prd/205987755#colourWayId-205987756')

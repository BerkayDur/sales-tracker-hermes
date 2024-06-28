"""Load Script: Populates the product table with the product information"""
from os import environ as CONFIG
import logging

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection

from extract_combined import extract_product_information
from helpers import get_connection, get_cursor

PRODUCT_READING_KEYS = set(
    ('url', 'product_name', 'product_code', 'website_id'))


def verify_keys(keys: list, required_keys: set) -> bool:
    """Verifies if all required keys are in keys."""
    return not required_keys - set(keys)


def insert_product_information(conn: connection, extracted_data: dict) -> bool:
    """Inserts product name and code into the database."""
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    if (not isinstance(extracted_data, dict)
            or not verify_keys(extracted_data, PRODUCT_READING_KEYS)):
        raise TypeError('Extracted data must be a dict with keys\
`url`, `product_name`, `product_code`, `website_id`.')

    logging.info("Inserting product data into the database")
    try:
        with get_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO PRODUCTS (website_id, url, product_code, product_name)
                VALUES (%s, %s, %s, %s)""",
                (extracted_data['website_id'], extracted_data['url'],
                 extracted_data['product_code'], extracted_data['product_name']))
            conn.commit()
            logging.info(
                "Product information successfully added into the database")
            return True
    except Exception:
        logging.error('Unable to insert product into database.')
        return False


def load_product_data(conn: connection, product_url: str) -> None:
    """Retrieves product information and inserts it into the database."""
    logging.info("Trying to load product information")
    extracted_data = extract_product_information(conn, product_url)

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
    connec = get_connection(CONFIG)
    URL = "ENTER URL HERE"
    load_product_data(connec, URL)

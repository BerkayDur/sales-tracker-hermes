"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""

from os import environ as CONFIG
import logging

from psycopg2.extensions import connection
from dotenv import load_dotenv
from urllib.parse import urlparse

from helpers import get_cursor, get_connection, configure_logging
from extract_from_asos import extract_product_information as extract_from_asos
from extract_from_patagonia import extract_product_information as extract_from_patagonia
from extract_from_other import extract_product_information as extract_from_other

EXTRACT_FUNCTIONS = {
    "asos": extract_from_asos,
    "patagonia": extract_from_patagonia
}


def identify_store(product_url: str) -> str | None:
    """Returns the store from the given URL."""
    if not isinstance(product_url, str):
        logging.error(
            "product_url passed to identify_store must be of type str")
        raise TypeError(
            "product_url passed to identify_store must be of type str")
    product_url = product_url.lower()
    for store_name in EXTRACT_FUNCTIONS:
        if store_name in product_url:
            logging.info("store name found in product url.")
            return store_name
    logging.info("store name not found in product url.")
    return None


def get_website_id(conn: connection, website_name: str) -> int:
    """get a website id from the database. Add the website if it is not found."""
    with get_cursor(conn) as cur:
        cur.execute(
            "SELECT website_id FROM websites WHERE website_name = %s", (website_name,))
        result = cur.fetchone()
        if result is None:
            cur.execute(
                "INSERT INTO websites (website_name) VALUES (%s) RETURNING website_id", (website_name,))
            website_id = cur.fetchone()["website_id"]
            conn.commit()
        else:
            website_id = result["website_id"]

    return website_id


def get_website_name(url: str) -> str:
    """Finds a website name from its url"""
    parsed_url = urlparse(url)
    domain_parts = parsed_url.netloc.split('.')
    if domain_parts[0] == 'www':
        domain_parts.pop(0)
    website_name = domain_parts[0]
    return website_name


def extract_product_information(conn: connection, product_url: str) -> tuple:
    """Given an URL identifies the store and calls the relevant extract file."""
    logging.info("Starting identify store from product url.")
    store_name = identify_store(product_url)
    if not store_name:
        logging.info(
            "Website not stored, running AI extract script for product url.")
        website_data = extract_from_other(product_url)
        website_data["website_id"] = get_website_id(
            conn, get_website_name(product_url))
        return website_data
    website_id = get_website_id(conn, store_name)
    if not website_id:
        logging.info("extract_product_information , website_id is null.")
        return None

    logging.info("Starting to run correct extract script for product url.")
    try:
        website_data = EXTRACT_FUNCTIONS[store_name](product_url)
        website_data["website_id"] = website_id
        logging.info("Successfully extract product information from website.")
        return website_data
    except Exception:
        logging.info("extract_product_information from product url failed!")
        return None


if __name__ == "__main__":
    load_dotenv()
    configure_logging()

    URL = "ENTER YOUR URL HERE."

    connec = get_connection(CONFIG)
    print(extract_product_information(connec, URL))

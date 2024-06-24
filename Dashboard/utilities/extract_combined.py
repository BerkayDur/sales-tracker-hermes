"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""
from os import environ as CONFIG

import logging
from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv

from helpers import get_cursor, get_connection
from extract_from_asos import extract_product_information as extract_from_asos

EXTRACT_FUNCTIONS = {
    'asos' : extract_from_asos
}

def identify_store(product_url: str) -> str | None:
    """Returns the store from the given URL."""
    if not isinstance(product_url, str):
        logging.error('product_url passed to identify_store must be of type str')
        raise TypeError('product_url passed to identify_store must be of type str')
    product_url = product_url.lower()
    for store_name in EXTRACT_FUNCTIONS.keys():
        if store_name in product_url:
            logging.info('store name found in product url.')
            return store_name
    logging.info('store name not found in product url.')
    return None

def get_website_id(conn: connection, website_name: str) -> int:
    '''get a website id from the database.'''
    with get_cursor(conn) as cur:
        cur.execute('SELECT website_id FROM websites WHERE website_name = %s', (website_name,))
        website_id = cur.fetchone()
    return website_id.get('website_id')


def extract_product_information(conn: connection, product_url: str) -> tuple:
    """Given an URL identifies the store and calls the relevant extract file."""
    logging.info('Starting identify store from product url.')
    store_name = identify_store(product_url)
    if not store_name:
        return None
    website_id = get_website_id(conn, store_name)
    if not website_id:
        return None

    logging.info('Starting to run correct extract script for product url.')
    try:
        website_data = EXTRACT_FUNCTIONS[store_name](product_url)
        website_data['website_id'] = website_id
        return website_data
    except ValueError:
        logging.info('extract from product url failed!')
        return None


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level='INFO')
    URL = "https://www.asos.com/asos-design/asos-design-disney-oversized-unisex-tee-in-off-white-with-mickey-mouse-graphic-prints/prd/205987755#colourWayId-205987756"
    # URL = 'https://www.asos.com/men/sale/cat/?cid=8409&ctaref=hp%7Cmw%7Cpromo%7Chero%7C1%7Cedit%7Csalelaunch&page=5'
    conn = get_connection(CONFIG)
    print(extract_product_information(conn, URL))

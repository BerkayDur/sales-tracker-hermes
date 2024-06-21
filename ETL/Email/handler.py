'''Contains the lambda handler for loading the product reading into database and
   sending an email alert to customers.'''

from os import environ as CONFIG
import logging

from helpers import get_connection, get_ses_client
from combined_load import write_new_price_entries_to_db
from email_service import PRODUCT_READING_KEYS, verify_keys, send_emails

def handler(_event, _context) -> None:
    '''Handler takes in product readings where price has decreased
    or product is on sale.

    Using this it emails customers and inserts the readings into the database.'''
    
    logging.basicConfig(level='INFO')

    if not _event.get('products'):
        logging.error('No product readings!')
        return {
            'status': 'No product entries!'
        }

    if not isinstance(_event['products'], list):
        logging.error('Product entries are not of type list.')
        return {
            'status': 'Product entries are not a list.'
        }

    _event['products'] = list(
        filter(lambda x: isinstance(x, dict) and verify_keys(x.keys(), PRODUCT_READING_KEYS),
               _event['products']))
    if len(_event['products']) == 0:
        logging.error('No product entries after cleaning!')
        return {
            'status': 'No product entires!'
        }
    logging.info('Successfully passed validations!')
    conn = get_connection(CONFIG)
    ses_client = get_ses_client(CONFIG)
    logging.info('Start entering new price entries to database.')
    write_new_price_entries_to_db(conn, _event['products'])
    logging.info('Successfully entered new price entries to database.')
    logging.info('Start notifying customers of price changes.')
    send_emails(conn, ses_client, _event['products'], PRODUCT_READING_KEYS)
    logging.info('Successfully notified customers of price changes.')

    return {
        'status': 'success. Data successfully inserted into database and customer notified!'
    }
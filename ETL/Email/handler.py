'''Contains the lambda handler for loading the product reading into database and
   sending an email alert to customers.'''

from os import environ as CONFIG
import logging
from datetime import datetime
from itertools import chain

from helpers import get_connection, get_ses_client
from combined_load import write_new_price_entries_to_db
from email_service import PRODUCT_READING_KEYS, verify_keys, send_emails


def handler(_event: list[list[dict]], _context) -> None:
    '''Handler takes in product readings where price has decreased
    or product is on sale.

    Using this it emails customers and inserts the readings into the database.'''

    logging.basicConfig(level='INFO')

    if not isinstance(_event, list):
        logging.error('_event must be a list of lists.')
        return {
            'status': 'Product entries are not a list of lists.'
        }
    _event = list(chain.from_iterable(_event))

    if not isinstance(_event, list):
        logging.error('Product entries are not of type list.')
        return {
            'status': 'Product entries are not a list.'
        }

    _event = list(
        filter(lambda x: isinstance(x, dict) and verify_keys(x.keys(), PRODUCT_READING_KEYS),
               _event))
    if len(_event) == 0:
        logging.error('No product entries after cleaning!')
        return {
            'status': 'No product entires!'
        }
    logging.info('Successfully passed validations!')
    logging.info('Start converting Datetime.')
    for i, product in enumerate(_event):
        try:
            _event[i]['reading_at'] = datetime.fromisoformat(product['reading_at'])
        except TypeError:
            _event.pop(i)
    logging.info('Successfully converted Datetime.')

    conn = get_connection(CONFIG)
    ses_client = get_ses_client(CONFIG)
    logging.info('Start entering new price entries to database.')
    write_new_price_entries_to_db(conn, _event)
    logging.info('Successfully entered new price entries to database.')
    logging.info('Start notifying customers of price changes.')
    send_emails(conn, ses_client, _event, PRODUCT_READING_KEYS)
    logging.info('Successfully notified customers of price changes.')

    return {
        'status': 'success. Data successfully inserted into database and customer notified!'
    }

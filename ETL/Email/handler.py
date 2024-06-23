'''Contains the lambda handler for loading the product reading into database and
   sending an email alert to customers.'''

from os import environ as CONFIG
import logging
from datetime import datetime
from itertools import chain


from dotenv import load_dotenv
from helpers import (get_connection, get_ses_client,
                     filter_on_current_price_less_than_previous_price)
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
        filter(lambda x: (isinstance(x, dict)
                          and verify_keys(x.keys(), PRODUCT_READING_KEYS)
                          and filter_on_current_price_less_than_previous_price(x)),
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

if __name__ == '__main__':
    load_dotenv()
    handler([[
    {
      "product_id": 1,
      "product_code": 206262254,
      "product_name": "ASOS DESIGN cotton cami top with front ties in white",
      "url": "https://www.asos.com/asos-design/asos-design-cotton-cami-top-with-front-ties-in-white/prd/206262254#ctaref-complementary%20items_1&featureref1-complementary%20items",
      "previous_price": 28,
      "current_price": 28,
      "is_on_sale": False,
      "reading_at": "2024-06-23.18:01:08"
    },
    {
      "product_id": 3,
      "product_code": 205186757,
      "product_name": "ASOS DESIGN laptop compartment canvas tote bag in natural  - NUDE",
      "url": "https://www.asos.com/asos-design/asos-design-laptop-compartment-canvas-tote-bag-in-natural-nude/prd/205186757#colourWayId-205186759",
      "previous_price": 9.6,
      "current_price": 9.6,
      "is_on_sale": True,
      "reading_at": "2024-06-23.18:01:08"
    }
  ]], None)
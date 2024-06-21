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

if __name__ == '__main__':
    print(len(list(chain.from_iterable([
  [
    {
      "product_id": 1,
      "product_code": 206022050,
      "product_name": "adidas Originals 72 slogan t-shirt in white",
      "url": "https://www.asos.com/adidas-originals/adidas-originals-72-slogan-t-shirt-in-white/prd/206022050#colourWayId-206022051",
      "previous_price": 30.99,
      "current_price": 13.5,
      "is_on_sale": True,
      "reading_at": "2024-06-21.15:18:43"
    },
    {
      "product_id": 2,
      "product_code": 206169129,
      "product_name": "New Balance 327 trainers in grey - exclusive to ASOS",
      "url": "https://www.asos.com/new-balance/new-balance-327-trainers-in-grey-exclusive-to-asos/prd/206169129#colourWayId-206169132",
      "previous_price": 120,
      "current_price": 110,
      "is_on_sale": False,
      "reading_at": "2024-06-21.15:18:43"
    },
    {
      "product_id": 3,
      "product_code": 205727541,
      "product_name": "ASOS DESIGN halter neck low back maxi sundress in black",
      "url": "https://www.asos.com/asos-design/asos-design-halter-neck-low-back-maxi-sundress-in-black/prd/205727541#colourWayId-205727547",
      "previous_price": 26,
      "current_price": 10.4,
      "is_on_sale": True,
      "reading_at": "2024-06-21.15:18:43"
    },
    {
      "product_id": 4,
      "product_code": 205454389,
      "product_name": "ASOS DESIGN relaxed t-shirt in grey with floral outline back print",
      "url": "https://www.asos.com/asos-design/asos-design-relaxed-t-shirt-in-grey-with-floral-outline-back-print/prd/205454389#colourWayId-205454390",
      "previous_price": None,
      "current_price": 9.8,
      "is_on_sale": True,
      "reading_at": "2024-06-21.15:18:43"
    },
    {
      "product_id": 5,
      "product_code": 205598222,
      "product_name": "ASOS DESIGN slim with linen suit in brown",
      "url": "https://www.asos.com/asos-design/asos-design-slim-with-linen-suit-in-brown/grp/206508195?ctaref=featured+product&featureref1=featured+product&#colourWayId-205598228&productId-205598222",
      "previous_price": None,
      "current_price": 35,
      "is_on_sale": False,
      "reading_at": "2024-06-21.15:18:43"
    }
  ],
  [
    {
      "product_id": 6,
      "product_code": 200497543,
      "product_name": "New Balance 327 trainers in off white/navy",
      "url": "https://www.asos.com/new-balance/new-balance-327-trainers-in-off-white-navy/prd/200497543#colourWayId-200497547",
      "previous_price": None,
      "current_price": 110,
      "is_on_sale": False,
      "reading_at": "2024-06-21.15:18:43"
    }
  ]
]))))
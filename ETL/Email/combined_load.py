'''This file contains source code to be able to insert product readings into a database
(very efficiently) from a list of products
'''

import logging
from itertools import chain

from psycopg2.extensions import connection

from helpers import get_cursor

def create_single_insert_format_string(num_of_values: int) -> str:
    '''Creates a single insert format string that can be used to insert a single row.'''
    if not isinstance(num_of_values, int):
        logging.error(
            'The number of values to construct insert format string form must be an integer.')
        raise TypeError(
            'The number of values to construct insert format string form must be an integer.')
    if num_of_values <= 0:
        logging.error(
            'The number of values to construct insert format string form must a positive integer.'
            )
        raise ValueError(
            'The number of values to construct insert format string form must a positive integer.'
            )
    return '(' + ',' .join(['%s'] * num_of_values) + ')'

def create_multiple_insert_format_string(num_of_values: int, single_insert_format: str) -> str:
    '''Creates a single insert format string that can be used to insert multiple rows with
    a single execute.'''
    if not isinstance(num_of_values, int):
        logging.error('The number of values to construct insert format string must an integer.')
        raise TypeError(
            'The number of values to construct insert format string form must be an integer.')
    if num_of_values <= 0:
        logging.error(
            'The number of values to construct insert format string form must a positive integer.'
            )
        raise ValueError(
            'The number of values to construct insert format string form must a positive integer.'
            )
    if not isinstance(single_insert_format, str):
        logging.error('the single insert format string that is repeated must be of type string.')
        raise TypeError('the single insert format string that is repeated must be of type string.')
    return ', '.join([single_insert_format]*num_of_values) + ';'

def write_new_price_entries_to_db(conn: connection,
                                  products: list[dict]) -> None:
    '''Writes new entries into the price_readings table in
    the database given a list of products.'''
    logging.info('Start performing type checks.')
    if not isinstance(conn, connection):
        logging.error('Database connection object must be of type connection.')
        raise TypeError('Database connection object must be of type connection.')
    if not isinstance(products, list):
        logging.error('Products must be a list.')
        raise TypeError('Products must be a list.')
    if len(products) == 0 or not all(isinstance(product, dict) for product in products):
        logging.error('Entries within the products list must be of type dict.')
        raise TypeError('Entries within the products list must be of type dict.')
    logging.info('Successfully pass type checking.')
    logging.info('Start formatting the data to be inserted.')
    data_to_be_inserted = tuple(
        (product['product_id'], product['reading_at'], product['current_price'])
            for product in products
    )
    logging.info('Successfully format the data to be inserted.')
    logging.info('Start formatting insert query.')
    formatted_input = create_multiple_insert_format_string(
        len(data_to_be_inserted),
        create_single_insert_format_string(len(data_to_be_inserted[0]))
    )
    query = 'INSERT INTO price_readings (product_id, reading_at, price) VALUES ' + formatted_input
    logging.info('Successfully format insert query.')
    logging.info('Start entering data into database.')
    with get_cursor(conn) as cur:
        cur.execute(query, tuple(chain.from_iterable(data_to_be_inserted)))
    conn.commit()
    logging.info('Successfully enter data into database.')

if __name__ == '__main__':
    logging.basicConfig(level='INFO')

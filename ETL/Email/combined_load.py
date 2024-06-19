'''This file contains source code to be able to insert product readings into a database
(very efficiently) from a list of products
'''

from itertools import chain

import psycopg2.extensions as psycopg2_types

from helpers import get_cursor

def create_single_insert_format_string(num_of_values: int) -> str:
    '''Creates a single insert format string that can be used to insert a single row.'''
    if not isinstance(num_of_values, int):
        raise TypeError('The number of values to construct insert format string form must be an integer.')
    if num_of_values <= 0:
        raise ValueError('The number of values to construct insert format string form must a positive integer.')
    return '(' + ',' .join(['%s'] * num_of_values) + ')'

def create_multiple_insert_format_string(num_of_values: int, single_insert_format: str) -> str:
    '''Creates a single insert format string that can be used to insert multiple rows with
    a single execute.'''
    if not isinstance(num_of_values, int):
        raise TypeError('The number of values to construct insert format string form must be an integer.')
    if num_of_values <= 0:
        raise ValueError('The number of values to construct insert format string form must a positive integer.')
    if not isinstance(single_insert_format, str):
        raise TypeError('the single insert format string that is repeated must be of type string.')
    return ', '.join([single_insert_format]*num_of_values) + ';'

def write_new_price_entries_to_db(conn: psycopg2_types.connection, products: list[dict]) -> None:
    '''Writes new entries into the price_readings table in the database given a list of products.'''
    if not isinstance(conn, psycopg2_types.connection):
        raise TypeError('database connection object must be of type connection.')
    if not isinstance(products, list):
        raise TypeError('products must be a list.')
    if len(products) == 0 or not all(isinstance(product, dict) for product in products):
        raise TypeError('entries within the products list must be of type dict.')
    data_to_be_inserted = [
        [product['product_id'], product['reading_at'], product['current_price']]
            for product in products
    ]

    formatted_input = create_multiple_insert_format_string(
        len(data_to_be_inserted),
        create_single_insert_format_string(len(data_to_be_inserted[0]))
    )
    query = 'INSERT INTO price_readings (product_id, reading_at, price) VALUES ' + formatted_input
    with get_cursor(conn) as cur:
        cur.execute(query, list(chain.from_iterable(data_to_be_inserted)))
    conn.commit()

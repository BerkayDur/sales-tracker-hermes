"A script to read the url, and product data from the database"
from os import _Environ, environ as ENV
import logging

from dotenv import load_dotenv
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor


def get_connection(config: _Environ) -> connection:
    "Establishes a connection with the database"
    return psycopg2.connect(
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        database=config["DB_NAME"]
    )


def get_cursor(conn: connection) -> cursor:
    "Returns a cursor for the database"
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def read_database(conn: connection):
    "Gets the required data from the database"
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    with get_cursor(conn) as cur:
        cur.execute("""SELECT DISTINCT ON (product_id) product_id, product_code, product_name, url, price
                    FROM products
                    LEFT JOIN price_readings USING (product_id)
                    ORDER BY product_id, reading_at DESC""")
        data = cur.fetchall()
    logging.info("Product details taken from database")
    logging.info(data)
    return data


def group_data(data: list[dict], processing_batch_size: int) -> list[list[dict]]:
    "Groups product data into lists up to a length of processing_batch_size"
    if not isinstance(processing_batch_size, int):
        raise TypeError("processing_batch_size must be an integer.")
    if not isinstance(data, list):
        raise TypeError("Input data must be a list.")
    if not all(isinstance(product, dict) for product in data):
        raise TypeError("All items in the list must be dictionaries.")

    product_outputs = []
    temp = []
    for product in data:
        temp.append(product)
        if len(temp) >= processing_batch_size:
            product_outputs.append(temp)
            temp = []
    if temp:
        product_outputs.append(temp)

    return product_outputs


def handler(_event=None, _context=None) -> dict[str, list[list[dict]]]:
    "Lambda handler function"
    db_conn = get_connection(ENV)
    product_data = [dict(row) for row in read_database(db_conn)]

    return {"output": group_data(
        product_data, int(ENV["PROCESSING_BATCH_SIZE"]))}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    load_dotenv()
    handler()

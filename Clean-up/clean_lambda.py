"A script to remove unsubscribed products from the database"

from os import _Environ, environ as ENV
import logging
import json

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor


def get_connection(config: _Environ) -> connection:
    "Establishes a connection with the database"
    return connect(
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

    return conn.cursor(cursor_factory=RealDictCursor)


def delete_unsubscribed(conn: connection, table: str) -> list[dict]:
    "Deletes info about the unsubscribed products from the database"
    if not isinstance(table, str):
        raise TypeError('table must be of type string')

    with get_cursor(conn) as cur:
        cur.execute(f"""
            DELETE FROM {table}
            WHERE product_id NOT IN (SELECT product_id FROM subscriptions)
            RETURNING *;""")
        data = cur.fetchall()
    conn.commit()
    logging.info(data)
    return [dict(i) for i in data]


def handler(_event, _context) -> str:
    "Main function which connects to the database and deletes the products"
    logging.basicConfig()
    db_conn = get_connection(ENV)
    deleted_readings = delete_unsubscribed(db_conn, "price_readings")
    deleted_products = delete_unsubscribed(db_conn, "products")

    return json.dumps({"deleted_readings": deleted_readings,
                       "deleted_products": deleted_products}, default=str)


if __name__ == "__main__":
    load_dotenv()
    print(handler(None, None))

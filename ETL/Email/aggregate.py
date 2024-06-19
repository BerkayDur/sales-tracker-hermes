from os import environ as CONFIG
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.extensions as psycopg2_types

sample_data = [
    {
        'product_id' : 0,
        'url' : 'https://www.asos.com/nike-running/nike-running-juniper-trail-2-gtx-trainers-in-grey/prd/205300355#colourWayId-205300357',
        'current_price' : 83.99,
        'prev_price' : 104.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now()
    },
    {
        'product_id' : 1,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 12.99,
        'prev_price' : 19.99,
        'is_on_sale' : False,
        'reading_at' : datetime.now()
    },
    {
        'product_id' : 2,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 19.99,
        'prev_price' : 19.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now()
    }
]


def get_connection(config: dict) -> psycopg2_types.connection:
    '''Get psycopg2 connection object to database'''
    return psycopg2.connect(
        host=config['DB_HOST'],
        port=config['DB_PORT'],
        dbname=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD']
    )

def get_cursor(connection: psycopg2_types.connection) -> psycopg2_types.cursor:
    '''Get a psycopg2 cursor using the configuration of a RealDictCursor'''
    return connection.cursor(cursor_factory=RealDictCursor)

def add_new_product_readings(data: list[dict]):
    ...

def get_customer_information(product_ids: list[int]) -> list[dict]:
    ...

if __name__ == '__main__':
    load_dotenv('.env')
    conn = get_connection(CONFIG)
    print(conn)
    with get_cursor(conn) as f:
        f.execute('SELECT * FROM price_readings;')
        data = f.fetchall()
        print(data)
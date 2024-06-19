from os import environ as CONFIG
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.extensions as psycopg2_types
import pandas as pd

sample_data = [
    {
        'product_id' : 1,
        'url' : 'https://www.asos.com/nike-running/nike-running-juniper-trail-2-gtx-trainers-in-grey/prd/205300355#colourWayId-205300357',
        'current_price' : 83.99,
        'prev_price' : 104.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now()
    },
    {
        'product_id' : 2,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 12.99,
        'prev_price' : 19.99,
        'is_on_sale' : False,
        'reading_at' : datetime.now()
    },
    {
        'product_id' : 3,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 18.99,
        'prev_price' : 19.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now()
    }
]

sample_data_pd = pd.DataFrame(sample_data)


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

def get_customer_information(connection: psycopg2_types.connection, product_ids: list[int]) -> pd.DataFrame:
    '''Gets the customer information for each each of the products ids as a DataFrame with columns:
                            product_id
                            email
                            price_threshold
    '''
    query = '''SELECT subscriptions.product_id, users.email, subscriptions.price_threshold
                FROM users
                JOIN subscriptions ON users.user_id = subscriptions.user_id
                WHERE subscriptions.product_id IN (''' + ','.join(str(product_id) for product_id in product_ids) + ');'
    with get_cursor(connection) as cur:
        cur.execute(query, product_ids)
        data = cur.fetchall()
    return pd.DataFrame(data)

def group_by_email(combined_data: pd.DataFrame, customer_email: str) -> pd.DataFrame:
    return combined_data[combined_data['email'] == customer_email]


def format_email_for_customer(combined_data: pd.DataFrame, customer_email: str) -> str:
    customer_data = combined_data[combined_data['email'] == customer_email]
    return customer_data


if __name__ == '__main__':
    load_dotenv('.env')
    conn = get_connection(CONFIG)
    product_ids = [data['product_id'] for data in sample_data] 
    customer_info = get_customer_information(conn, product_ids)
    merged_data = customer_info.merge(sample_data_pd, on=['product_id'], how='left')
    # print(format_email_for_customer(merged_data, 'user3@example.com'))
    emails = set(merged_data['email'])
    for email in emails:
        print(group_by_email(merged_data, email))
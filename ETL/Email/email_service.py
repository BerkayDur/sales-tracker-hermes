'''Contains the source code to be able to email
customers on a price decrease / sale of their tracked items.'''

from os import environ as CONFIG
from datetime import datetime

from dotenv import load_dotenv
import psycopg2.extensions as psycopg2_types
import pandas as pd
from mypy_boto3_ses import SESClient

from helpers import get_connection, get_cursor, get_ses_client, is_ses
from combined_load import create_single_insert_format_string


PRODUCT_READING_KEYS = set(('product_id', 'url', 'current_price',
                            'previous_price', 'is_on_sale',
                            'reading_at', 'product_name'))

sample_data = [
    {
        'product_id' : 1,
        'url' : 'https://www.asos.com/nike-running/nike-running-juniper-trail\
-2-gtx-trainers-in-grey/prd/205300355#colourWayId-205300357',
        'current_price' : 83.99,
        'previous_price' : 104.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now(),
        'product_name' : 'Nike Running Juniper Trail 2 GTX Trainers in Grey'
    },
    {
        'product_id' : 2,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-\
6-pack-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 340.99,
        'previous_price' : 350.99,
        'is_on_sale' : True, 
        'reading_at' : datetime.now(),
        'product_name' : 'Nike training everyday lightweight 6 pack no show socks in black'
    },
    {
        'product_id' : 3,
        'url' : 'https://www.asos.com/nike-training/nike-training-everyday-lightweight-6-pack\
-no-show-socks-in-black/prd/205607655#colourWayId-205607656',
        'current_price' : 18.99,
        'previous_price' : 19.99,
        'is_on_sale' : True,
        'reading_at' : datetime.now(),
        'product_name' : 'Falcon'
    }
]

sample_data_pd = pd.DataFrame(sample_data)

def verify_keys(keys: list, required_keys: set) -> bool:
    '''Verifies if all required keys are in keys.'''
    return not required_keys - set(keys)

def get_customer_information(
        conn: psycopg2_types.connection,
        product_ids: list[int]) -> pd.DataFrame:
    '''Gets the customer information for each each of the products ids as a DataFrame with columns:
                            product_id
                            email
                            price_threshold'''
    if not isinstance(conn, psycopg2_types.connection):
        raise TypeError('conn must be a psycopg2 connection object.')
    if not isinstance(product_ids, list):
        raise TypeError('product_ids must be a list.')
    if len(product_ids) == 0:
        raise ValueError('list product_ids cannot be empty.')
    if not all(isinstance(product_id, int) for product_id in product_ids):
        raise TypeError('All elements of product_ids must be an int.')
    query = f'''SELECT subscriptions.product_id, users.email, subscriptions.price_threshold
                FROM users
                JOIN subscriptions ON users.user_id = subscriptions.user_id
                WHERE subscriptions.product_id
                IN {create_single_insert_format_string(len(product_ids))};'''
    with get_cursor(conn) as cur:
        cur.execute(query, product_ids)
        data = cur.fetchall()
    return pd.DataFrame(data)

def get_merged_customer_and_product_reading_table(
        customer_information: pd.DataFrame,
        product_reading: pd.DataFrame) -> pd.DataFrame:
    '''merges the customer and product reading tables and filters only the relevant rows that:
            1. have passed the customers price threshold
            2. are on sale'''
    if not isinstance(customer_information, pd.DataFrame):
        raise TypeError('customer_information must be a pandas DataFrame.')
    if not isinstance(product_reading, pd.DataFrame):
        raise TypeError('product_reading must be a pandas DataFrame.')
    merged = customer_information.merge(product_reading, on=['product_id'], how='left')
    return merged[(merged['current_price'] <= merged['price_threshold']) | (merged['is_on_sale'])]

def group_by_email(
        data: pd.DataFrame,
        email: str) -> pd.DataFrame:
    '''Group the data table rows by an email.'''
    if not isinstance(data, pd.DataFrame):
        raise TypeError('data must be a pandas DataFrame.')
    if not isinstance(email, str):
        raise TypeError('email must be string containing the email to filter by.')
    return data[data['email'] == email]


def format_email_from_data_frame(
        row_data: pd.Series) -> pd.Series:
    '''Map a row of combined product reading and customer data into a
    row containing an email_type and message.'''
    website_name = 'ASOS'    ##### To be changed when we have more websites!!!


    if not isinstance(row_data, pd.Series):
        raise TypeError('row_data must be a pandas Series.')
    email_type = None
    sale_and_thres = False
    if row_data['price_threshold'] is not None:
        if row_data['current_price'] <= row_data['price_threshold']:
            email_type = 'threshold'
    if row_data['is_on_sale']:
        if email_type:
            sale_and_thres = True
        if not email_type:
            email_type = 'sale'



    message = (f"({website_name}) <a href='{row_data['url']}'>{row_data['product_name']}</a> " +
               f"was £{row_data['previous_price']}, now £{row_data['current_price']}" +
               f"{' (ON SALE)' if sale_and_thres else ''}.")
    return pd.Series([email_type, message], index=['email_type', 'message'])


def get_subject(
        email_types: pd.Series) -> str:
    '''Create an email subject based on the email types.'''
    if not isinstance(email_types, pd.Series):
        raise TypeError('email_types must be a pandas Series.')
    has_threshold = any(email_types == 'threshold')
    has_sale = any(email_types == 'sale')
    if has_threshold and has_sale:
        return 'Tracked products price decrease!'
    if has_threshold:
        return 'Tracked product(s) below threshold!'
    return 'Tracked product(s) on sale!'

def get_html_unordered_list(
        content_to_place_in_list: list[str]) -> str:
    '''Get an unordered html list containing the correct tags from a list of strings.'''
    if not isinstance(content_to_place_in_list, list):
        raise TypeError('content_to_place_in_list must be a list.')
    if not all(isinstance(content, str) for content in content_to_place_in_list):
        raise TypeError('Elements in content_to_place_in_list must be of type str.')
    if len(content_to_place_in_list) == 0:
        return ''
    return '<ul><li>' + '</li><li>'.join(content_to_place_in_list) + '</li></ul>'

def create_email_body(
        email_data: pd.DataFrame) -> str:
    '''Create the body of an email based on the data for each customer.'''
    if not isinstance(email_data, pd.DataFrame):
        raise TypeError('email_data must be a pandas DataFrame.')
    sale_message = get_html_unordered_list(
        email_data[email_data['email_type'] == 'sale']['message'].to_list())
    threshold_message = get_html_unordered_list(
        email_data[email_data['email_type'] == 'threshold']['message'].to_list())

    if sale_message:
        sale_message = '<p>The following tracked products are on SALE!</p>' + sale_message
    if threshold_message:
        threshold_message = ('<p>The following tracked products have crossed your threshold!</p>'
                             + threshold_message)
    return threshold_message + sale_message


def get_formatted_email(
        customer_data: pd.DataFrame) -> dict:
    '''Formats customer data into a dictionary containing the relevant data for an email.'''
    if not isinstance(customer_data, pd.DataFrame):
        raise TypeError('customer_data must be a pandas DataFrame.')
    applied_data = customer_data.apply(format_email_from_data_frame, axis=1)
    return {
        'recipient' : customer_data['email'].values[0],
        'subject' : get_subject(applied_data['email_type']),
        'body' : create_email_body(applied_data)
    }


def get_email_list(
        emails: pd.Series,
        ses_client: SESClient) -> set:
    '''Given a Series of emails, return of these emails that are verified on AWS.'''
    if not isinstance(emails, pd.Series):
        raise TypeError('emails must be a pandas Series.')
    if not is_ses(ses_client):
        raise TypeError('ses_client must be a BOTO3 SES Client.')
    verified_emails = ses_client.list_verified_email_addresses()['VerifiedEmailAddresses']
    return set(emails) & set(verified_emails)

def send_email_to_client(
        ses_client: SESClient,
        email_content: dict[str]) -> bool:
    '''Email a client using a pre-formatted email given by dict of keys:
                1. recipient
                2. subject
                3. body
    Returns True if status code is 2XX else False.'''
    if not is_ses(ses_client):
        raise TypeError('ses_client must be a BOTO3 SES Client.')
    if not isinstance(email_content, dict):
        raise TypeError('email_content must be of type dict.')
    if not all(isinstance(content, str) for content in email_content):
        raise TypeError('Elements of email_content must be of type str.')
    res = ses_client.send_email(
        Source='trainee.berkay.dur@sigmalabs.co.uk',
        Destination={
            'ToAddresses': [
                'trainee.berkay.dur@sigmalabs.co.uk', ##Should eventually be: email_content['recipient']
            ]
        },
        Message={
            'Subject': {
                'Data': email_content['subject'],
                'Charset': 'utf-8'
            },
            'Body': {
                'Html': {
                    'Data': email_content['body'],
                    'Charset': 'utf-8'
                }
            }
        }
    )
    return (res['ResponseMetadata']['HTTPStatusCode'] >= 200
            and res['ResponseMetadata']['HTTPStatusCode'] < 300)

def send_emails(
        conn: psycopg2_types.connection,
        ses_client: SESClient,
        product_readings: list[dict],
        product_keys: set) -> bool:
    '''Performs the entire pipeline to send emails to clients based on product readings.'''
    if not isinstance(product_readings, list):
        return False
    product_readings = list(
        filter(lambda x: isinstance(x, dict) and verify_keys(x.keys(), product_keys),
               product_readings))
    if len(product_readings) == 0:
        return False


    product_ids = [data['product_id'] for data in product_readings]

    customer_info = get_customer_information(conn, product_ids)
    merged_data = get_merged_customer_and_product_reading_table(
        customer_info, pd.DataFrame(product_readings))

    ########### this mail_list will be used in practice over the one after it.
    # mail_list = get_email_list(merged_data['email'], ses_client)
    mail_list = set(merged_data['email'])

    mail_list = [get_formatted_email(group_by_email(merged_data, email)) for email in mail_list]
    return all(send_email_to_client(ses_client, content) for content in mail_list)

if __name__ == '__main__':
    load_dotenv('.env')
    connection = get_connection(CONFIG)
    client = get_ses_client(CONFIG)

    send_emails(connection, client, sample_data, PRODUCT_READING_KEYS)

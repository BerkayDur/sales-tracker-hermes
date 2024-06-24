'''Contains the source code to be able to email
customers on a price decrease / sale of their tracked items.'''

from os import environ as CONFIG
from datetime import datetime
import logging
from math import isnan

from dotenv import load_dotenv
from psycopg2.extensions import connection
import pandas as pd
import mypy_boto3_ses.client as ses_client

from helpers import get_connection, get_cursor, get_ses_client, is_ses
from combined_load import create_single_insert_format_string


PRODUCT_READING_KEYS = set(('product_id', 'url', 'current_price',
                            'previous_price', 'is_on_sale',
                            'reading_at', 'product_name'))


def verify_keys(keys: list, required_keys: set) -> bool:
    '''Verifies if all required keys are in keys.'''
    return not required_keys - set(keys)

def get_customer_information(
        conn: connection,
        product_ids: list[int]) -> pd.DataFrame:
    '''Gets the customer information for each each of the products ids as a DataFrame with columns:
                            product_id
                            email
                            price_threshold'''
    if not isinstance(conn, connection):
        logging.error('conn must be a psycopg2 connection object.')
        raise TypeError('conn must be a psycopg2 connection object.')
    if not isinstance(product_ids, list):
        logging.error('products_ids must be a list.')
        raise TypeError('product_ids must be a list.')
    if len(product_ids) == 0:
        logging.error('list product_ids cannot be empty.')
        raise ValueError('list product_ids cannot be empty.')
    if not all(isinstance(product_id, int) for product_id in product_ids):
        logging.error('All elements of products_ids must be an int.')
        raise TypeError('All elements of product_ids must be an int.')
    query = f'''SELECT subscriptions.product_id, users.email, subscriptions.price_threshold
                FROM users
                JOIN subscriptions USING (user_id)
                WHERE subscriptions.product_id
                IN {create_single_insert_format_string(len(product_ids))};'''
    with get_cursor(conn) as cur:
        cur.execute(query, product_ids)
        data = cur.fetchall()

    return pd.DataFrame(data)


def filter_merged_table(merged_table: pd.DataFrame) -> pd.DataFrame:
    '''filters the merged customer and product reading dataframe for a few cases:
        1. The current price is less than the previous price (if threshold doesn't exist)
                and only if the product is on sale.
        2. The current price is less than a threshold (if exists).
    
    NOTE that the customer this filtering doesn't care too much about an explicit sale if
    the current previous hasn't decreased (I.e., product may change to being on sale without
    a price decreases).'''
    if not isinstance(merged_table, pd.DataFrame):
        raise TypeError('merged_table parameter in filter_merged_table must be of type DataFrame.')

    threshold_filter = merged_table['price_threshold'].isnull()
    non_null_threshold_table = merged_table[~threshold_filter]
    non_null_threshold_table.loc[:,'price_threshold'] = (
        non_null_threshold_table.loc[:,'price_threshold'].astype(float))
    curr_less_threshold_filter = (non_null_threshold_table['current_price']
                                  <= non_null_threshold_table['price_threshold'])
    prev_less_threshold_filter = (non_null_threshold_table['previous_price']
                                  <= non_null_threshold_table['price_threshold'])
    threshold_compare_merged_table = (
        merged_table[~threshold_filter][(curr_less_threshold_filter)
                                        & (~prev_less_threshold_filter)])
    prev_price_filter = merged_table['previous_price'].isnull()
    curr_less_prev_filter = (
        merged_table[threshold_filter &  ~prev_price_filter]['current_price']
        < merged_table[threshold_filter &  ~prev_price_filter]['previous_price'])
    product_on_sale_filter = merged_table[threshold_filter &  ~prev_price_filter]['is_on_sale']
    prev_compare_merged_table = (
        merged_table[threshold_filter &  ~prev_price_filter]
            [curr_less_prev_filter & product_on_sale_filter])
    return pd.concat([threshold_compare_merged_table, prev_compare_merged_table])

def get_merged_customer_and_product_reading_table(
        customer_information: pd.DataFrame,
        product_reading: pd.DataFrame) -> pd.DataFrame:
    '''merges the customer and product reading tables and filters only the relevant rows that:
            1. have passed the customers price threshold
            2. are on sale'''
    if not isinstance(customer_information, pd.DataFrame):
        logging.error('customer_information must be a pandas DataFrame.')
        raise TypeError('customer_information must be a pandas DataFrame.')
    if not isinstance(product_reading, pd.DataFrame):
        logging.error('product_reading must be a pandas DataFrame.')
        raise TypeError('product_reading must be a pandas DataFrame.')
    merged = customer_information.merge(product_reading, on=['product_id'], how='left')
    merged = filter_merged_table(merged)
    return merged


def group_by_email(
        data: pd.DataFrame,
        email: str) -> pd.DataFrame:
    '''Group the data table rows by an email.'''
    if not isinstance(data, pd.DataFrame):
        logging.error('data must be a pandas DataFrame.')
        raise TypeError('data must be a pandas DataFrame.')
    if not isinstance(email, str):
        logging.error('email must be a string containing the email to filter by.')
        raise TypeError('email must be a string containing the email to filter by.')
    return data[data['email'] == email]


def format_email_from_data_frame(
        row_data: pd.Series) -> pd.Series:
    '''Map a row of combined product reading and customer data into a
    row containing an email_type and message.'''
    website_name = 'ASOS'    ##### To be changed when we have more websites!!!


    if not isinstance(row_data, pd.Series):
        logging.error('row_data must be a pandas Series.')
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

    message = f"({website_name}) <a href='{row_data['url']}'>{row_data['product_name']}</a> "
    if not row_data['previous_price'] or (isinstance(row_data['previous_price'], (int, float))
                                           and isnan(row_data['previous_price'])):
        message += f"now £{row_data['current_price']}"
    else:
        message += f"was £{row_data['previous_price']}, now £{row_data['current_price']}"

    message += f"{' (ON SALE)' if sale_and_thres else ''}."

    return pd.Series([email_type, message], index=['email_type', 'message'])


def get_subject(
        email_types: pd.Series) -> str:
    '''Create an email subject based on the email types.'''
    if not isinstance(email_types, pd.Series):
        logging.error('email_types must be a pandas Series.')
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
        logging.error('content_to_place_in_list must be of type list.')
        raise TypeError('content_to_place_in_list must be of type list.')
    if not all(isinstance(content, str) for content in content_to_place_in_list):
        logging.error('Elements in content_to_place_in_list must be of type str.')
        raise TypeError('Elements in content_to_place_in_list must be of type str.')
    if len(content_to_place_in_list) == 0:
        return ''
    return '<ul><li>' + '</li><li>'.join(content_to_place_in_list) + '</li></ul>'

def create_email_body(
        email_data: pd.DataFrame) -> str:
    '''Create the body of an email based on the data for each customer.'''
    if not isinstance(email_data, pd.DataFrame):
        logging.error('email_data must be a pandas DataFrame.')
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
        logging.error('customer_data must be a pandas DataFrame.')
        raise TypeError('customer_data must be a pandas DataFrame.')
    applied_data = customer_data.apply(format_email_from_data_frame, axis=1)
    return {
        'recipient' : customer_data['email'].values[0],
        'subject' : get_subject(applied_data['email_type']),
        'body' : create_email_body(applied_data)
    }


def get_email_list(
        emails: pd.Series,
        ses: ses_client) -> set:
    '''Given a Series of emails, return of these emails that are verified on AWS.'''
    if not isinstance(emails, pd.Series):
        logging.error('emails must be a pandas Series.')
        raise TypeError('emails must be a pandas Series.')
    if not is_ses(ses):
        logging.error('ses_client must be a BOTO3 SES Client.')
        raise TypeError('ses_client must be a BOTO3 SES Client.')
    verified_emails = ses.list_verified_email_addresses()['VerifiedEmailAddresses']
    return set(emails) & set(verified_emails)

def send_email_to_client(
        ses: ses_client,
        email_content: dict[str]) -> bool:
    '''Email a client using a pre-formatted email given by dict of keys:
                1. recipient
                2. subject
                3. body
    Returns True if status code is 2XX else False.'''
    if not is_ses(ses):
        logging.error('ses_client must be a BOTO3 SES Client.')
        raise TypeError('ses_client must be a BOTO3 SES Client.')
    if not isinstance(email_content, dict):
        logging.error('email_content must be of type dict.')
        raise TypeError('email_content must be of type dict.')
    if not all(isinstance(content, str) for content in email_content):
        logging.error('Elements of email_content must be of type str.')
        raise TypeError('Elements of email_content must be of type str.')
    res = ses.send_email(
        Source='trainee.berkay.dur@sigmalabs.co.uk',
        Destination={
            'ToAddresses': [
                email_content['recipient'],
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
        conn: connection,
        ses: ses_client,
        product_readings: list[dict],
        product_keys: set) -> bool:
    '''Performs the entire pipeline to send emails to clients based on product readings.'''
    logging.info('filtering send_emails input to remove bad inputs.')
    if not isinstance(product_readings, list):
        logging.error(
            'elements of product_readings in send_emails are not of type list, exit early.')
        return False
    product_readings = list(
        filter(lambda x: isinstance(x, dict) and verify_keys(x.keys(), product_keys),
               product_readings))
    if len(product_readings) == 0:
        logging.error('No product_readings, exit early.')
        return False
    logging.info('finish filtering send_emails input.')

    product_ids = [data['product_id'] for data in product_readings]

    logging.info('get customer information from database.')
    customer_info = get_customer_information(conn, product_ids)
    if len(customer_info) == 0:
        logging.error('No customer information, exit early.')
        return False
    logging.info('Successfully got customer information from the database.')
    logging.info('Start merging customer data and products readings.')
    merged_data = get_merged_customer_and_product_reading_table(
        customer_info, pd.DataFrame(product_readings))
    if len(merged_data) == 0:
        logging.error('No merged data, exit early.')
        return False
    logging.info('Successfully merged customer data and products readings.')

    logging.info('Getting list of email-verified customers.')
    mail_list = get_email_list(merged_data['email'], ses)
    if len(mail_list) == 0:
        logging.error("Customer emails aren't verified, exit early.")
        return False
    logging.info('Successfully get list of email-verified customers.')

    logging.info('Start formatting emails for each customer.')
    mail_list = [get_formatted_email(group_by_email(merged_data, email)) for email in mail_list]
    logging.info('Successfully format emails for each customer.')
    return all(send_email_to_client(ses, content) for content in mail_list)

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    load_dotenv('.env')
    connection_obj = get_connection(CONFIG)
    client = get_ses_client(CONFIG)
    send_emails(connection_obj, client, [[{}, {}]], PRODUCT_READING_KEYS)

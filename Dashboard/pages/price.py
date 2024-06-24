"""Price tracker page for streamlit"""

from os import environ as CONFIG
import logging
from dotenv import load_dotenv

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from navigation import make_sidebar

from utilities.helpers import get_cursor, get_connection
from utilities.load import load_product_data

def can_parse_as_float(to_check: any) -> bool:
    try:
        float(to_check)
        return True
    except ValueError:
        return False

def get_supported_websites(conn) -> list:
    """Gets a list of supported websites."""
    with get_cursor(conn) as cur:
        cur.execute('SELECT website_name from websites;')
        websites = cur.fetchall()
    return [website['website_name'] for website in websites]

def get_user_id(conn, email: str) -> int | None:
    with get_cursor(conn) as cur:
        cur.execute('SELECT user_id from users WHERE email = %s;', (email,))
        user_id = cur.fetchone()
    return user_id.get('user_id')

def get_product_id(conn, url: str) -> int | None:
    with get_cursor(conn) as cur:
        cur.execute('SELECT product_id from products WHERE url = %s;', (url,))
        product_id = cur.fetchone()
    return product_id.get('product_id')

def is_subscription_in_table(conn, user_id: int, product_id: int) -> bool:
    with get_cursor(conn) as cur:
        cur.execute('''SELECT * FROM subscriptions
                        WHERE user_id = %s AND product_id = %s''',
                        (user_id, product_id))
        counts = cur.fetchone()
    return counts is not None

def insert_subscription_into_db(conn, user_id: int, product_id: int, price_threshold: float| int | None) -> bool:
    try:
        with get_cursor(conn) as cur:
            cur.execute('''INSERT INTO subscriptions
                         (user_id, product_id, price_threshold)
                        VALUES (%s, %s, %s);''', (user_id, product_id, price_threshold))
            conn.commit()
        return True
    except Exception:
        return False

def update_db_to_subscribe(config: dict, product_url: str, price_threshold: bool | None, user_email: str) -> bool:
    conn = get_connection(config)
    user_id = get_user_id(conn, user_email)
    if not user_id:
        st.warning('User not validated. Please try again!')
        return False
    product_id = get_product_id(conn, product_url)
    if not product_id:
        st.warning('Unexpected error, please try again later.')
        return False
    if is_subscription_in_table(conn, user_id, product_id):
        st.warning('You are already subscribed to this product!')
        return False
    st.success('New subscription added!')
    return insert_subscription_into_db(conn, user_id, product_id, price_threshold)

def subscribe_to_product(config: dict, product_url: str, price_threshold: bool | None) -> bool:
    """adds a product to the database and return True if successful
    (or if product is already in the database), else False."""
    try:
        load_product_data(config, product_url)
    except (TypeError, ValueError):
        st.warning('Invalid URL, please enter a URL from one of the supported websites!')
        return False
    try:
        return  update_db_to_subscribe(config, product_url, price_threshold, st.session_state['email'])
    except (TypeError, ValueError):
        st.warning('Unable to subscribe to product!')
        return False

def price_tracker_page(config: dict) -> None:
    """Product Price Tracker Page"""
    conn = get_connection(config)
    st.title("Product Price Tracker")
    websites = get_supported_websites(conn)

    with st.expander("List of Supported websites", expanded=True):
        for website in websites:
            st.write(website)
    with st.expander("Subscribe to new product", expanded=True):
        with st.form('subscribe_to_product', clear_on_submit=True, border=False):
            product_url = st.text_input("Enter the product URL:")
            price_threshold = st.text_input("Enter a threshold", placeholder="Can be left empty")
            if st.form_submit_button("Track Price", type="primary"):
                if not product_url:
                    st.error("You must enter a URL.")
                elif price_threshold != '' and not can_parse_as_float(price_threshold):
                    st.warning('Threshold must be a number (or empty).')
                elif product_url:
                    subscribe_to_product(config, product_url, price_threshold)
    



if __name__ == "__main__":
    load_dotenv('../.env')
    logging.basicConfig(level="INFO")
    st.query_params["page"] = "price"
    make_sidebar()
    price_tracker_page(CONFIG)

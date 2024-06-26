from os import _Environ, environ as CONFIG
import logging

import streamlit as st
from psycopg2.extensions import connection

from navigation import make_sidebar

from helpers import get_cursor, get_connection
from load import load_product_data

def can_parse_as_float(to_check: any) -> bool:
    """Determines if a value can be parsed as a float.
    Returns True on success, else False."""
    try:
        float(to_check)
        return True
    except (ValueError, TypeError):
        logging.error("Input can't be parsed as a float")
        return False

def get_supported_websites(conn: connection) -> list:
    """Gets a list of supported websites."""
    with get_cursor(conn) as cur:
        cur.execute("SELECT website_name from websites;")
        websites = cur.fetchall()
    return [website["website_name"] for website in websites]

def get_user_id(conn: connection, email: str) -> int | None:
    """Get a user id from the database based on an email."""
    with get_cursor(conn) as cur:
        cur.execute("SELECT user_id from users WHERE email = %s;", (email,))
        user_id = cur.fetchone()
    return user_id.get("user_id")

def get_product_id(conn: connection, url: str) -> int | None:
    """Gets the products id from the database given a url."""
    with get_cursor(conn) as cur:
        cur.execute("SELECT product_id from products WHERE url = %s;", (url,))
        product_id = cur.fetchone()
    return product_id.get("product_id")


def is_subscription_in_table(conn: connection, user_id: int, product_id: int) -> bool:
    """Determines if a user is subscribed to a particular product."""
    with get_cursor(conn) as cur:
        cur.execute("""SELECT * FROM subscriptions
                        WHERE user_id = %s AND product_id = %s""",
                    (user_id, product_id))
        counts = cur.fetchone()
    return counts is not None

def insert_subscription_into_db(
        conn: connection, user_id: int, product_id: int,
        price_threshold: float | int | None) -> bool:
    """Inserts a new subscription into the subscriptions table.
    Returns True on success, else False."""
    try:
        with get_cursor(conn) as cur:
            cur.execute("""INSERT INTO subscriptions
                         (user_id, product_id, price_threshold)
                        VALUES (%s, %s, %s);""", (user_id, product_id, price_threshold))
            conn.commit()
        return True
    except Exception as e:
        st.write(e)
        return False



def update_db_to_subscribe(
        config: _Environ, product_url: str, price_threshold: bool | None, user_email: str) -> bool:
    """Inserts a subscription into a database, if it doesn't already exist.
    Returns True on success, else False"""
    conn = get_connection(config)
    user_id = get_user_id(conn, user_email)
    if not user_id:
        logging.error("User not validated. Please try again!")
        st.warning("User not validated. Please try again!")
        return False
    product_id = get_product_id(conn, product_url)
    if not product_id:
        logging.error("Unexpected error, please try again later.")
        st.warning("Unexpected error, please try again later.")
        return False
    if is_subscription_in_table(conn, user_id, product_id):
        logging.error("You are already subscribed to this product!")
        st.warning("You are already subscribed to this product!")
        return True
    logging.info("New subscription added!")
    st.success("New subscription added!")
    return insert_subscription_into_db(conn, user_id, product_id, price_threshold)


def subscribe_to_product(config: _Environ, product_url: str, price_threshold: bool | None) -> bool:
    """adds a product to the database and return True if successful
    (or if product is already in the database), else False."""
    try:
        load_product_data(config, product_url)
    except (TypeError, ValueError):
        logging.error(
            "Invalid URL, please enter a URL from one of the supported websites!")
        st.warning(
            "Invalid URL, please enter a URL from one of the supported websites!")
        return False
    try:
        if price_threshold == "":
            price_threshold = None
        return update_db_to_subscribe(config, product_url,
                                      price_threshold, st.session_state["email"])
    except (TypeError, ValueError):
        logging.error("Unable to subscribe to product!")
        st.warning("Unable to subscribe to product!")
        return False

def add_product_page(config: _Environ):
    conn = get_connection(config)
    websites = get_supported_websites(conn)
    st.title('Add new Subscription')
    with st.container(border=True,):
        with st.form("subscribe_to_product", clear_on_submit=True, border=False):
            product_url = st.text_input("Enter the product URL:")
            price_threshold = st.text_input(
                "Enter a threshold (£):", placeholder="Can be left empty")
            if st.form_submit_button("Track Product", type="primary"):
                if not product_url:
                    logging.error("You must enter a URL.")
                    st.error("You must enter a URL.")
                elif price_threshold != "" and not can_parse_as_float(price_threshold):
                    logging.error("Threshold must be a number (or empty).")
                    st.warning("Threshold must be a number (or empty).")
                elif can_parse_as_float(price_threshold) and float(price_threshold) <= 0:
                    st.warning('Price Threshold must be positive!')
                else:
                    subscribe_to_product(config, product_url, price_threshold)
    with st.expander("List of Supported websites", expanded=True):
        for website in websites:
            st.write(website.title())

if __name__ == '__main__':
    make_sidebar()
    add_product_page(CONFIG)
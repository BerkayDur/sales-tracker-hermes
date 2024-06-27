'''Contains the add product page for streamlit dashboard.'''
from os import environ as CONFIG
import logging

import streamlit as st
from psycopg2.extensions import connection

from navigation import make_sidebar # pylint: disable=import-error
from helpers import ( # pylint: disable=import-error
    get_connection, can_parse_as_float,
    get_supported_websites,
    update_db_to_subscribe
)
from load import load_product_data # pylint: disable=import-error

def subscribe_to_product(conn: connection, product_url: str, price_threshold: bool | None) -> bool:
    """adds a product to the database and return True if successful
    (or if product is already in the database), else False."""
    try:
        load_product_data(conn, product_url)
    except Exception:
        logging.error(
            "Invalid URL, please enter a URL from one of the supported websites!")
        st.warning(
            "Invalid URL, please enter a URL from one of the supported websites!")
        return False
    try:
        if price_threshold == "":
            price_threshold = None
        update_db_status = update_db_to_subscribe(conn, product_url,
                                      price_threshold, st.session_state["email"])
        if update_db_status['status']:
            st.success(update_db_status['message'])
        else:
            st.warning(update_db_status['message'])
    except Exception:
        logging.error("Unable to subscribe to product!")
        st.warning("You are already subscribed to this product")
        return False
    return True

def add_product_page(conn: connection) -> None:
    """Add Product Page"""
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
                    subscribe_to_product(conn, product_url, price_threshold)
    with st.expander("List of Supported websites", expanded=True):
        for website in websites:
            st.write(website.title())

if __name__ == '__main__':
    connec = get_connection(CONFIG)
    make_sidebar()
    add_product_page(connec)

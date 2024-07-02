"""Contains the add product page for streamlit dashboard."""
from os import environ as CONFIG
import logging

import streamlit as st
from psycopg2.extensions import connection

from navigation import make_sidebar  # pylint: disable=import-error
from helpers import (  # pylint: disable=import-error
    get_connection, can_parse_as_float,
    get_supported_websites,
    update_db_to_subscribe
)
from load import load_product_data  # pylint: disable=import-error
from custom_styling import apply_custom_styling  # pylint: disable=import-error


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
        if update_db_status["status"]:
            logging.info(
                "Successfully updates database to add user, product subscription.")
            st.success(update_db_status["message"])
        else:
            logging.error(
                "Failed to update database to add user, product subscription.")
            st.warning(update_db_status["message"])
    except Exception:
        logging.error("User is already subscribed to this product.")
        st.warning("You are already subscribed to this product.")
        return False
    return True


def add_product_page(conn: connection) -> None:
    """Add Product Page"""
    websites = get_supported_websites(conn)
    st.markdown('<h2 class="pageTitle">Add New Subscription</h2>',
                unsafe_allow_html=True)
    st.write("")
    with st.container(border=True,):
        with st.form("subscribe_to_product", clear_on_submit=True, border=False):
            product_url = st.text_input("**Paste the product link:**")
            st.write("")
            price_threshold = st.text_input(
                "**Alert me when this product is below:** **:orange[*]**", placeholder="£")
            st.markdown(
                """<span style="font-size:0.8rem; position:relative; top:-1rem;">**:orange[*]**
                Leave this empty to be alerted on all price decreases</span>""",
                unsafe_allow_html=True)
            if st.form_submit_button("Track this Product", type="primary"):
                if not product_url:
                    logging.error("User must enter a URL.")
                    st.error("You must enter a product link.")
                elif price_threshold != "" and not can_parse_as_float(price_threshold):
                    logging.error("Threshold must be a number (or empty).")
                    st.warning("Threshold must be a number (or empty).")
                elif can_parse_as_float(price_threshold) and float(price_threshold) <= 0:
                    logging.error(
                        "Price threshold entered by user must be positive.")
                    st.warning("Price Threshold must be positive!")
                else:
                    subscribe_to_product(conn, product_url, price_threshold)
    with st.expander("**See supported websites**", expanded=False):
        for website in websites:
            st.markdown(website)


if __name__ == "__main__":
    connec = get_connection(CONFIG)
    apply_custom_styling()
    make_sidebar()
    add_product_page(connec)

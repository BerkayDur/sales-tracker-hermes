"""Price tracker page for streamlit"""

import logging

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from navigation import make_sidebar


def price_tracker_page() -> None:
    """Product Price Tracker Page"""
    st.title("Product Price Tracker")

    with st.expander("List of Compatible websites", expanded=True):
        st.write("ASOS")

    product_url = st.text_input("Enter the product URL:")

    if st.button("Track Price", type="primary"):
        if product_url:
            subscribe(product_url)
        else:
            st.error("Please enter a valid product URL.")


def subscribe(product_url: str) -> DeltaGenerator:
    """Tracks product"""
    exist = check_url_exists(product_url)
    if exist:
        return st.success(
            "Product url is already being tracked. You have been subscribed.")

    price = get_price(product_url)
    if price:
        return st.success(f"The current price of the product is: {price}")
    return st.error("Unable to fetch the price. Please check the URL.")


def check_url_exists(product_url: str) -> bool:
    """Check if the url exists"""
    product_url += "url"
    return False


def get_price(product_url: str) -> str:
    """Gets the price from the product_url"""
    product_url += "url"
    return "£20"


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    st.query_params["page"] = "price"
    make_sidebar()

    price_tracker_page()

"""Price tracker page for streamlit"""

from os import _Environ, environ as CONFIG
import logging
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import altair as alt
from psycopg2.extensions import connection


from navigation import make_sidebar
from utilities.helpers import get_cursor, get_connection
from utilities.load import load_product_data
from utilities.ses_get_emails import get_ses_client, get_ses_emails


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


def get_subscribed_products(config: _Environ, email: str) -> list[dict]:
    """Get a list of all products subscribed by user, email."""
    conn = get_connection(config)
    with get_cursor(conn) as cur:
        cur.execute("""SELECT product_id, website_name, url, product_name, price_threshold
                    FROM websites
                    JOIN products USING (website_id)
                    JOIN subscriptions USING (product_id)
                    JOIN users USING (user_id)
                    WHERE email = %s""", (email,))
        subscribed_products = cur.fetchall()
    return subscribed_products


def get_price_readings(config: _Environ, product_id: int) -> pd.DataFrame | None:
    """Get a pandas DataFrame of all price readings for a particular product."""
    conn = get_connection(config)
    with get_cursor(conn) as cur:
        cur.execute(
            """SELECT * FROM price_readings WHERE product_id = %s;""", (product_id,))
        price_readings = cur.fetchall()
    if not price_readings:
        return None
    price_readings = pd.DataFrame(price_readings)
    price_readings["price"] = price_readings["price"].apply(float)
    return price_readings


def get_encode_price_reading(
        price_readings: pd.DataFrame, price_threshold: float | None) -> alt.ChartDataType:
    """Encode the price readings for a particular product as an altair Chart."""
    price_reading_at = price_readings[[
        "price", "reading_at"]].sort_values(by="reading_at")
    fake_new_data = price_reading_at.iloc[[-1]]
    fake_new_data["reading_at"] = datetime.now()
    price_reading_at = pd.concat([price_reading_at, fake_new_data])
    chart = alt.Chart(price_reading_at).encode(
        x="reading_at:T",
        y="price"
    )
    if price_threshold is not None:
        max_reading = price_reading_at["reading_at"].max()
        min_reading = price_reading_at["reading_at"].min()
        price_threshold_df = pd.DataFrame([{"reading_at": min_reading, "price": price_threshold},
                                           {"reading_at": max_reading, "price": price_threshold}])
        chart_2 = alt.Chart(price_threshold_df).encode(
            x="reading_at:T",
            y="price",
            color=alt.value("#FF0000")
        )
        return chart_2.mark_line() + chart.mark_point() + chart.mark_line()
    return chart.mark_point() + chart.mark_line()


def display_subscribed_product(config: _Environ, product_information: dict) -> None:
    """For a particular product, get the price readings and display a container
    for that product, containing relevant information."""
    price_readings = get_price_readings(
        config, product_information["product_id"])

    with st.container(border=True):
        st.write("**%s** - **[%s](%s)**" % (product_information["website_name"],
                                            product_information["product_name"],
                                            product_information["website_name"]))
        if price_readings is not None:
            if can_parse_as_float(product_information['price_threshold']):
                product_information['price_threshold'] = float(product_information["price_threshold"])
            encoded_price_readings = get_encode_price_reading(
                price_readings, product_information["price_threshold"])
            st.altair_chart(encoded_price_readings)
        else:
            st.write("No data to display")
        st.write(price_readings)


def price_tracker_page(config: _Environ) -> None:
    """Product Price Tracker Page"""
    conn = get_connection(config)
    st.title("Product Price Tracker")
    websites = get_supported_websites(conn)

    with st.expander("List of Supported websites", expanded=True):
        for website in websites:
            st.write(website)

    with st.expander("Subscribe to new product", expanded=True):
        with st.form("subscribe_to_product", clear_on_submit=True, border=False):
            product_url = st.text_input("Enter the product URL:")
            price_threshold = st.text_input(
                "Enter a threshold", placeholder="Can be left empty")
            if st.form_submit_button("Track Price", type="primary"):
                if not product_url:
                    logging.error("You must enter a URL.")
                    st.error("You must enter a URL.")
                elif price_threshold != "" and not can_parse_as_float(price_threshold):
                    logging.error("Threshold must be a number (or empty).")
                    st.warning("Threshold must be a number (or empty).")
                else:
                    subscribe_to_product(config, product_url, price_threshold)
        ses_client = get_ses_client(config)
    with st.expander(label="Email Alerts!"):
        if st.session_state['email'] not in get_ses_emails(ses_client, method='verified'):
            if st.button('Click here to sign up to email alerts.'):
                st.warning('Sending verification, please check your inbox.')


    subscribed_to_products = get_subscribed_products(
        config, st.session_state["email"])
    st.write(subscribed_to_products)
    for product in subscribed_to_products:
        display_subscribed_product(config, product)


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    load_dotenv("../.env")
    make_sidebar()

    price_tracker_page(CONFIG)

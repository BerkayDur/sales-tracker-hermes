"""Price tracker page for streamlit"""

from os import environ as CONFIG
import logging
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import pandas as pd
import altair as alt

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
    except Exception as e:
        st.write(e)
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
        return True
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
        if price_threshold == '':
            price_threshold = None
        return  update_db_to_subscribe(config, product_url, price_threshold, st.session_state['email'])
    except (TypeError, ValueError):
        st.warning('Unable to subscribe to product!')
        return False


def get_subscribed_products(config: dict, email: str) -> None:
    conn = get_connection(config)
    with get_cursor(conn) as cur:
        cur.execute('''SELECT product_id, website_name, url, product_name, price_threshold
                    FROM websites
                    JOIN products USING (website_id)
                    JOIN subscriptions USING (product_id)
                    JOIN users USING (user_id)
                    WHERE email = %s''', (email,))
        subscribed_products = cur.fetchall()
    return subscribed_products

def get_price_readings(config, product_id: int) -> pd.DataFrame | None:
    conn = get_connection(config)
    with get_cursor(conn) as cur:
        cur.execute('''SELECT * FROM price_readings WHERE product_id = %s;''', (product_id,))
        price_readings = cur.fetchall()
    if not price_readings:
        return None
    price_readings = pd.DataFrame(price_readings)
    price_readings['price'] = price_readings['price'].apply(float)
    return price_readings

def get_encode_price_reading(price_readings: pd.DataFrame, price_threshold: float | None) -> alt.ChartDataType:
    price_reading_at = price_readings[['price', 'reading_at']].sort_values(by='reading_at')
    fake_new_data = price_reading_at.iloc[[-1]]
    fake_new_data['reading_at'] = datetime.now()
    price_reading_at = pd.concat([price_reading_at, fake_new_data])
    chart = alt.Chart(price_reading_at).encode(
        x = 'reading_at:T',
        y = 'price'
    )
    if price_threshold is not None:
        max_reading = price_reading_at['reading_at'].max()
        min_reading = price_reading_at['reading_at'].min()
        price_threshold_df = pd.DataFrame([{'reading_at': min_reading, 'price': price_threshold},
                                           {'reading_at': max_reading, 'price': price_threshold}])
        chart_2 = alt.Chart(price_threshold_df).encode(
            x = 'reading_at:T',
            y = 'price',
            color = alt.value('#FF0000')
        )
        return chart_2.mark_line() + chart.mark_point() + chart.mark_line()
    return chart.mark_point() + chart.mark_line()


def display_subscribed_product(config, product_information: dict) -> None:
    price_readings = get_price_readings(config, product_information['product_id'])

    with st.container(border=True):
        st.write('**%s** - **[%s](%s)**'% (product_information['website_name'], product_information['product_name'], product_information['url']), )
        if price_readings is not None:
            encoded_price_readings = get_encode_price_reading(price_readings, float(product_information['price_threshold']))
            st.altair_chart(encoded_price_readings)

        else:
            st.write('No data to display')
        st.write(price_readings)


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
    subscribed_to_products = get_subscribed_products(config, st.session_state['email'])
    st.write(subscribed_to_products)
    for product in subscribed_to_products:
        display_subscribed_product(config, product)



if __name__ == "__main__":
    load_dotenv('../.env')
    logging.basicConfig(level="INFO")
    st.query_params["page"] = "price"
    make_sidebar()
    price_tracker_page(CONFIG)

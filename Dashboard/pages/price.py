"""Price tracker page for streamlit"""

from os import _Environ, environ as CONFIG
import logging
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
import streamlit_nested_layout
import pandas as pd
import altair as alt
from psycopg2.extensions import connection


from navigation import make_sidebar
from helpers import (
    get_cursor, get_connection,
    can_parse_as_float, get_user_id,
    get_subscribed_products
)






def get_price_readings(conn: connection, product_id: int) -> pd.DataFrame | None:
    """Get a pandas DataFrame of all price readings for a particular product."""
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
    title = alt.TitleParams('Price over Time', anchor='middle')
    chart = alt.Chart(price_reading_at, title=title).encode(
        x="reading_at:T",
        y="price"
    )
    if price_threshold is not None:
        max_reading = price_reading_at["reading_at"].max()
        min_reading = price_reading_at["reading_at"].min()
        price_threshold_df = pd.DataFrame([{"reading_at": min_reading, "price": price_threshold},
                                           {"reading_at": max_reading, "price": price_threshold}])
        threshold_chart = alt.Chart(price_threshold_df)
        threshold_line_enc = threshold_chart.encode(
            x=alt.X("reading_at:T", title="Taken at"),
            y=alt.Y("price", title = "Price (£)"),
            color=alt.value("#FF0000"),
        )
        return threshold_line_enc.mark_line() + chart.mark_point() + chart.mark_line()
    return chart.mark_point() + chart.mark_line()

def change_threshold_in_db(conn: connection, new_threshold: float | None, product_id: int, email: str) -> None:
    user_id = get_user_id(conn, email)
    with get_cursor(conn) as cur:
        cur.execute('''UPDATE subscriptions
                        SET price_threshold = %s
                        WHERE user_id = %s
                        AND product_id = %s''', (new_threshold, user_id, product_id))
        conn.commit()
    

def change_threshold(conn: connection, product_information: dict) -> None:
    text_input_placeholder = None
    if product_information['price_threshold'] is not None:
        text_input_placeholder = f"£{float(product_information['price_threshold']):.2f}"
    new_threshold = st.text_input('Enter a new Threshold (£):',
                                    placeholder=text_input_placeholder,
                                    help='Can be left empty to remove threshold!',
                                    key=f'new_threshold_value_{product_information['product_id']}')
    st.write('')
    if st.button('Update Price Alert', key=f'new_threshold_submit_{product_information['product_id']}'):
        valid_threshold = False
        if new_threshold == '':
            new_threshold = None
            valid_threshold = True
        elif can_parse_as_float(new_threshold):
            new_threshold = float(new_threshold)
            if new_threshold > 0:
                valid_threshold = True
        if not valid_threshold and new_threshold == product_information['price_threshold']:
            st.warning('New threshold is the same as the old threshold.')
        elif valid_threshold:
            change_threshold_in_db(conn, new_threshold, product_information['product_id'], st.session_state['email'])
            st.rerun()
        elif not valid_threshold and isinstance (new_threshold, float):
            st.warning('Threshold must be a positive number!')
        else:
            st.warning('Invalid threshold, please try again!')

def unsubscribe_from_product_in_db(conn: connection, product_id: int, email: str) -> None:
    user_id = get_user_id(conn, email)
    with get_cursor(conn) as cur:
        cur.execute('''DELETE FROM subscriptions
                        WHERE product_id = %s
                        AND user_id = %s''', (product_id, user_id))
        conn.commit()

def unsubscribe_from_product(conn: connection, product_information: int) -> None:
    if st.button('Unsubscribe', key=f'unsubscribe_button_{product_information['product_id']}'):
        unsubscribe_from_product_in_db(conn, product_information['product_id'], st.session_state['email'])
        st.rerun()

def product_price_change(price_readings: pd.DataFrame) -> int:
    '''returns an emoji representing the emoji regarding the price.'''
    if len(price_readings) == 1:
        return 0
    price_readings_sorted_by_time = price_readings.sort_values(by='reading_at', ascending=False)[:2].reset_index()
    if price_readings_sorted_by_time.loc[0]['price'] > price_readings_sorted_by_time.loc[1]['price']:
        return 1
    elif price_readings_sorted_by_time.loc[0]['price'] == price_readings_sorted_by_time.loc[1]['price']:
        return 0
    return -1

def get_price_change_emoji(price_change_enum: int) -> str:
    if price_change_enum == 0:
        return '➖'
    elif price_change_enum == 1:
        return '📈'
    return '📉'

def get_price_change_colour(price_change_enum: int) -> str:
    if price_change_enum == 0:
        return 'orange'
    elif price_change_enum == 1:
        return 'red'
    return 'green'

def display_subscribed_product(conn: connection, product_information: dict) -> None:
    """For a particular product, get the price readings and display a container
    for that product, containing relevant information."""
    price_readings = get_price_readings(
        conn, product_information["product_id"])
    expander = st.expander(f'Fetching data for {product_information['product_name']}')
    if price_readings is not None:
        current_price = float(price_readings[
                    price_readings['reading_at'] == price_readings['reading_at'].max()]['price'])
        price_change_enum = product_price_change(price_readings)
        expander = st.expander(f'**£:{get_price_change_colour(price_change_enum)}[{current_price:.2f}]** - {product_information['product_name']}', icon=get_price_change_emoji(price_change_enum))
    with expander:
        st.write('')
        if price_readings is not None:
            col1, col2 = st.columns(2)
            
            if can_parse_as_float(product_information['price_threshold']):
                product_information['price_threshold'] = float(product_information["price_threshold"])
            encoded_price_readings = get_encode_price_reading(
                price_readings, product_information["price_threshold"])
            with col1:
                inner_col_1, inner_col_2 = st.columns([5,10])
                with inner_col_1:
                    st.link_button('Go to Product', url=product_information['url'])
                with inner_col_2:
                    unsubscribe_from_product(conn, product_information)
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                with st.container(border=True):
                    st.write('')
                    change_threshold(conn, product_information)
                    st.write('')
            with col2:
                st.altair_chart(encoded_price_readings)
        else:
            st.write("Fetching data... Please wait.")


def price_tracker_page(conn: connection) -> None:
    """Product Price Tracker Page"""


    subscribed_to_products = get_subscribed_products(
        conn, st.session_state["email"])
    if subscribed_to_products:
        st.title('Tracked products:')
        subscribed_to_products.sort(key=lambda x:x['product_id'])
        websites = list(set(product['website_name'] for product in subscribed_to_products))
        websites.sort()
        for website in websites:
            st.write('')
            with st.expander(f'**{website}**'.title()):
                for product in subscribed_to_products:
                    if product['website_name'] == website:
                        display_subscribed_product(conn, product)
    else:
        st.warning('You are not subscribed to any products, please subscribe above!')


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    load_dotenv("../.env")
    make_sidebar()

    connec = get_connection(CONFIG)
    price_tracker_page(connec)

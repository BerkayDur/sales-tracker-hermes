"""Price tracker page for the streamlit dashboard"""

from os import environ as CONFIG
import logging
from datetime import datetime

from dotenv import load_dotenv
import streamlit as st
import streamlit_nested_layout # pylint: disable=unused-import
import pandas as pd
import altair as alt
from psycopg2.extensions import connection


from navigation import make_sidebar # pylint: disable=import-error
from helpers import ( # pylint: disable=import-error
    get_cursor, get_connection,
    can_parse_as_float, get_user_id,
    get_subscribed_products,
    get_price_readings
)
from custom_styling import apply_custom_styling # pylint: disable=import-error

def get_encode_price_reading(
        price_readings: pd.DataFrame, price_threshold: float | None) -> alt.ChartDataType:
    """Encode the price readings for a particular product as an altair Chart."""
    price_reading_at = price_readings[[
        "price", "reading_at"]].sort_values(by="reading_at")
    fake_new_data = price_reading_at.iloc[[-1]]
    fake_new_data["reading_at"] = datetime.now()
    price_reading_at = pd.concat([price_reading_at, fake_new_data])

    title = alt.TitleParams('Historical Price', anchor='middle')
    chart = alt.Chart(price_reading_at, title=title).encode(
        x=alt.X("reading_at:T", title="Time", axis=alt.Axis(labels=False)),
        y=alt.Y("price", title="Price (£)", scale=alt.Scale(zero=False))
        )
    if price_threshold is not None:
        max_reading = price_reading_at["reading_at"].max()
        min_reading = price_reading_at["reading_at"].min()
        price_threshold_df = pd.DataFrame([
            {"reading_at": min_reading, "price": price_threshold},
            {"reading_at": max_reading, "price": price_threshold, 'text': 'Alert Threshold'}])
        threshold_chart = alt.Chart(price_threshold_df)
        threshold_line_enc = threshold_chart.encode(
            x=alt.X("reading_at:T", title="Time"),
            y=alt.Y("price", title = "Price (£)"),
            color=alt.value("#FF0000"),
            text='text'
        )
        return (threshold_line_enc.mark_text(
            align='right', baseline='middle',
            dx=75, dy=0).transform_filter(alt.datum.text is not None)
                + threshold_line_enc.mark_line()
                + chart.mark_point(color="black")
                + chart.mark_line(color="black"))
    return chart.mark_point(color='black') + chart.mark_line(color="black")

def change_threshold_in_db(
        conn: connection, new_threshold: float | None, product_id: int, email: str) -> None:
    '''Given a new price threshold, this function modifies the subscription entry to that
    new threshold.'''
    user_id = get_user_id(conn, email)
    with get_cursor(conn) as cur:
        cur.execute('''UPDATE subscriptions
                        SET price_threshold = %s
                        WHERE user_id = %s
                        AND product_id = %s''', (new_threshold, user_id, product_id))
        conn.commit()

def change_threshold(conn: connection, product_information: dict) -> None:
    '''Contains the streamlit display logic for changing the threshold in the dashboard.'''
    text_input_placeholder = '£'
    if product_information['price_threshold'] is not None:
        text_input_placeholder = f"£{float(product_information['price_threshold']):.2f}"
    st.markdown('''
        <div style="position:relative;top:-1rem;">
        <p style="font-size:1.3rem; color: var(--orange); font-weight:600;">Update Price Alert</p>
        </div>''', unsafe_allow_html=True)

    new_threshold = st.text_input('**Alert me when this product is below:** **:orange[*]**' ,
                                    placeholder=text_input_placeholder,
                                    key=f'new_threshold_value_{product_information['product_id']}')
    st.markdown('''
        <span style="font-size:0.8rem; position:relative; top:-1rem;">
                **:orange[*]** Leave this empty to be alerted on all price decreases
        </span>''', unsafe_allow_html=True)
    col1, col2 = st.columns([5,3])
    with col1:
        price_alert_update = st.button(
            'Update Price Alert',
            key=f'new_threshold_submit_{product_information['product_id']}')
    with col2:
        unsubscribe_from_product(conn, product_information['product_id'])
    if price_alert_update:
        valid_threshold = False
        if new_threshold == '':
            new_threshold = None
            valid_threshold = True
        elif can_parse_as_float(new_threshold):
            new_threshold = float(new_threshold)
            if new_threshold > 0:
                valid_threshold = True
        if not valid_threshold and new_threshold == product_information['price_threshold']:
            logging.warning('New threshold is the same as the old threshold.')
            st.warning('New threshold is the same as the old threshold.')
        elif valid_threshold:
            change_threshold_in_db(conn, new_threshold,
                                   product_information['product_id'], st.session_state['email'])
            st.rerun()
        elif not valid_threshold and isinstance (new_threshold, float):
            logging.warning('Threshold must be a positive number!')
            st.warning('Threshold must be a positive number!')
        else:
            logging.warning('Invalid threshold, please try again!')
            st.warning('Invalid threshold, please try again!')

def unsubscribe_from_product_in_db(conn: connection, product_id: int, email: str) -> None:
    '''Unsubscribe a user from a product, given product_id and user email.'''
    user_id = get_user_id(conn, email)
    with get_cursor(conn) as cur:
        cur.execute('''DELETE FROM subscriptions
                        WHERE product_id = %s
                        AND user_id = %s''', (product_id, user_id))
        conn.commit()

def unsubscribe_from_product(conn: connection, product_id: int) -> None:
    '''contains the streamlit display logic for unsubscribing a user from a product,
    given product id..'''
    if st.button('Unsubscribe', key=f'unsubscribe_button_{product_id}'):
        unsubscribe_from_product_in_db(conn, product_id,
                                       st.session_state['email'])
        st.rerun()

def product_price_change(price_readings: pd.DataFrame) -> int:
    '''returns an emoji representing the emoji regarding the price.'''
    if len(price_readings) == 1:
        return 0
    price_readings_sorted_by_time = (
        price_readings.sort_values(by='reading_at', ascending=False)[:2].reset_index())
    if (price_readings_sorted_by_time.loc[0]['price']
        > price_readings_sorted_by_time.loc[1]['price']):
        return 1
    if (price_readings_sorted_by_time.loc[0]['price']
        == price_readings_sorted_by_time.loc[1]['price']):
        return 0
    return -1

def get_price_change_emoji(price_change_enum: int) -> str:
    '''returns an emoji based on an enumerated price change value.'''
    if price_change_enum == 0:
        return '➖'
    if price_change_enum == 1:
        return '📈'
    return '📉'

def get_price_change_colour(price_change_enum: int) -> str:
    '''returns text colour based on an enumerated price change value.'''
    if price_change_enum == 0:
        return 'orange'
    if price_change_enum == 1:
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
        expander = st.expander(
            f'**£:{get_price_change_colour(price_change_enum)}[{current_price:.2f}]**\
- {product_information['product_name']}', icon=get_price_change_emoji(price_change_enum))
    with expander:
        st.write('')
        if price_readings is not None:
            col1, col2 = st.columns(2)
            if can_parse_as_float(product_information['price_threshold']):
                product_information['price_threshold'] = (
                    float(product_information["price_threshold"]))
            encoded_price_readings = get_encode_price_reading(
                price_readings, product_information["price_threshold"])
            with col1:
                st.link_button('Go to product', url=product_information['url'])
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
        st.markdown('<h2 class="pageTitle">Track Your Products</h2>', unsafe_allow_html=True)
        subscribed_to_products.sort(key=lambda x:x['product_id'])
        websites = list(set(product['website_name'] for product in subscribed_to_products))
        websites.sort()
        for website in websites:
            st.write('')
            with st.expander(f'**{website}**'):
                for product in subscribed_to_products:
                    if product['website_name'] == website:
                        display_subscribed_product(conn, product)
    else:
        st.warning(
        'You are not subscribed to track any product, please subscribe to track price changes.')


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    load_dotenv("../.env")
    st.set_page_config(layout='wide')
    apply_custom_styling()
    make_sidebar()
    connec = get_connection(CONFIG)
    price_tracker_page(connec)

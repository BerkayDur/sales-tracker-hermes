"""Login page for streamlit"""

from os import _Environ, environ as ENV
import logging
import re

import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection

EMAIL = r"(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"


def get_connection(config: _Environ) -> connection:
    "Establishes a connection with the database"
    return connect(
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        database=config["DB_NAME"]
    )


def authenticate(email) -> tuple | None:
    """Find email in database"""
    logging.info("Searching for %s in database", email)
    load_dotenv()
    conn = get_connection(ENV)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT email FROM users
            WHERE email = %s""", (email,))
        data = cur.fetchone()
    return data


def add_email(email):
    """Add email to database"""
    logging.info("Adding %s to database", email)
    load_dotenv()
    conn = get_connection(ENV)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT email FROM users
            WHERE email = %s""", (email,))
        data = cur.fetchone()
    return data


def login_page() -> None:
    """Login page"""
    st.title("Login Page")

    st.write("trainee.faris.abulula@sigmalabs.co.uk")
    email = st.text_input(
        "Please enter your email to access the website:")

    if st.button("Login"):
        logging.info("Login button clicked with %s", email)
        if authenticate(email):
            logging.info("%s logged in", email)
            st.success(f"Welcome! You are logged in with email: {email}")
            st.session_state.logged_in = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error(f"Invalid email address {email}. Please try again.")

    st.write("---")

    st.title("Sign up")

    email = st.text_input(
        "Please enter your email to sign up to the website:")

    if st.button("Sign up"):
        logging.info("Sign up button clicked")
        st.write(email)
        if re.search(EMAIL, email):
            st.success(f"Welcome! You are logged in with email: {email}")
            st.session_state.logged_in = True
            st.session_state.email = email
            st.rerun()
        else:
            st.error("Invalid email address. Please try again.")


def main() -> None:
    """Checking login information"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        st.switch_page("pages/1_price.py")
    else:
        login_page()


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    main()

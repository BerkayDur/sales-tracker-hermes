"""Login page for streamlit"""

from os import _Environ, environ as ENV
import logging
import re
from time import sleep

import streamlit as st
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extensions import connection

from navigation import make_sidebar

EMAIL_PATTERN = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""


def get_connection(config: _Environ) -> connection:
    "Establishes a connection with the database"
    return connect(
        user=config["DB_USER"],
        password=config["DB_PASSWORD"],
        host=config["DB_HOST"],
        port=config["DB_PORT"],
        database=config["DB_NAME"]
    )


def authenticate(conn: connection, email: str) -> tuple | None:
    """Find email in database"""
    logging.info("Searching for %s in database", email)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT email FROM users
            WHERE email = %s""", (email,))
        data = cur.fetchone()
    return data


def add_email(conn: connection, email: str) -> tuple | None:
    """Add email to database"""
    logging.info("Adding %s to database", email)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users(email)
            VALUES (%s)
            RETURNING email""", (email,))
        data = cur.fetchone()
        conn.commit()
    return data


def login_page(config: _Environ, email_pattern: str) -> None:
    """Login page"""
    st.title("Login Page")

    login_email = st.text_input(
        "Please enter your email to access the website:",
        placeholder="email",
    )
    if st.button("Login", type="primary"):
        logging.info("Login button clicked with %s", login_email)
        conn = get_connection(config)
        if authenticate(conn, login_email):
            login(login_email)
        else:
            logging.error("Invalid email address. Please sign up.")
            st.error("Invalid email address. Please sign up.")

    st.write("---")

    st.title("Sign up")

    signup_email = st.text_input(
        "Please enter your email to sign up to the website:",
        placeholder="email"
    )
    if st.button("Sign up", type="primary"):
        logging.info("Sign up button clicked with %s", signup_email)
        conn = get_connection(config)
        if authenticate(conn, signup_email):
            logging.error(
                "The email %s is already registered. Please log in.", signup_email)
            st.error(
                f"The email {signup_email} is already registered. Please log in.")
        elif re.match(email_pattern, signup_email):
            add_email(conn, signup_email)
            login(signup_email)
        else:
            logging.error("Invalid email address. Please try again.")
            st.error("Invalid email address. Please try again.")


def login(email: str) -> None:
    """Login and move to next page"""
    st.session_state.logged_in = True
    st.session_state.email = email
    logging.info("Welcome! You are logged in with email: %s", email)
    st.success(f"Welcome! You are logged in with email: {email}")
    sleep(0.5)
    st.switch_page("pages/price.py")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    make_sidebar()
    load_dotenv()

    login_page(ENV, EMAIL_PATTERN)

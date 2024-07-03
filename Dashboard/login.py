"""Login page for streamlit"""

from os import _Environ, environ as ENV
import logging
import re
from time import sleep

import streamlit as st
from bcrypt import gensalt, hashpw, checkpw
from dotenv import load_dotenv
from psycopg2.extensions import connection

from helpers import get_connection
from navigation import make_sidebar
from custom_styling import apply_custom_styling

EMAIL_PATTERN = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""  # pylint: disable=line-too-long


def get_email(conn: connection, email: str) -> tuple[str, str] | None:
    """Find email in database"""
    logging.info("Searching for %s in database", email)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT email, CONVERT_FROM(password, 'UTF8') FROM users
            WHERE email = %s""", (email,))
        data = cur.fetchone()
    return data


def add_email(conn: connection, email: str, password: bytes) -> tuple | None:
    """Add email to database"""
    logging.info("Adding %s to database", email)
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO users(email, password)
            VALUES (%s, %s)
            RETURNING *""", (email, password))
        data = cur.fetchone()
        conn.commit()
    return data


def login(email: str) -> None:
    """Login and move to next page"""
    st.session_state.logged_in = True
    st.session_state.email = email
    logging.info("Welcome! You are logged in with email: %s", email)
    st.success(f"Welcome! You are logged in with email: {email}")
    sleep(0.5)
    st.switch_page("pages/price.py")


def login_page(config: _Environ, email_pattern: str) -> None:
    """Login page"""
    st.header("Sign in")

    login_email = st.text_input("Please enter your email address:")
    login_password = st.text_input(
        "Please enter your password:", type="password").encode("utf-8")

    if st.button("Login", type="primary"):
        logging.info("Login button clicked with %s", login_email)
        conn = get_connection(config)
        data = get_email(conn, login_email)
        if data:
            email, password = data
            if checkpw(login_password, password.encode("utf-8")):
                login(email)
            logging.error("Invalid password. Please try again.")
            st.error("Invalid password. Please try again.")
        else:
            logging.error("Invalid email address. Please sign up.")
            st.error("Invalid email address. Please sign up.")

    st.write("---")

    st.header("Sign up")

    signup_email = st.text_input("Please enter your email address: ")
    signup_password = st.text_input(
        "Please enter your password: ", type="password").encode("utf-8")

    if st.button("Sign up", type="primary"):
        logging.info("Sign up button clicked with %s", signup_email)
        conn = get_connection(config)
        if get_email(conn, signup_email):
            logging.error(
                "The email %s is already registered. Please log in.", signup_email)
            st.error(
                f"The email {signup_email} is already registered. Please log in.")
        elif re.match(email_pattern, signup_email):
            hash_pw = hashpw(signup_password, gensalt())
            add_email(conn, signup_email, hash_pw)
            login(signup_email)
        else:
            logging.error("Invalid email address. Please try again.")
            st.error("Invalid email address. Please try again.")


if __name__ == "__main__":
    logging.basicConfig(level="INFO")
    apply_custom_styling()
    make_sidebar()
    load_dotenv()

    login_page(ENV, EMAIL_PATTERN)

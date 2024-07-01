"""This file contains functions that are used throughout this directory""""""
from os import _Environ
import logging

from psycopg2 import connect
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from boto3 import client as boto_client
from botocore.client import BaseClient
from mypy_boto3_ses.client import SESClient as ses_client
import requests
from bs4 import BeautifulSoup
import pandas as pd


DEFAULT_REQUEST_TIMEOUT_SECONDS = 30


def get_connection(config: _Environ) -> connection:
    """Establishes a connection with the database."""
    logging.info("Trying to connect to Database.")
    return connect(
        user=config["DB_USER"],
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        password=config["DB_PASSWORD"],
        port=config["DB_PORT"]
    )


def get_cursor(conn: connection) -> cursor:
    """Returns a cursor for the database."""
    if not isinstance(conn, connection):
        logging.error(
            "A cursor can only be constructed from a Psycopg2 connection object")
        raise TypeError(
            "A cursor can only be constructed from a Psycopg2 connection object")
    logging.info("Creating a Psycopg2 cursor.")
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def configure_logging() -> None:
    """Sets up basic logger"""
    return logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def get_product_page(url: str, headers: dict) -> str | None:
    """Fetch the HTML content of a product page from a given URL."""
    if not isinstance(url, str):
        logging.error("URL must be of type string in get_product_page.")
        raise TypeError("URL must be of type string.")
    if not isinstance(headers, dict):
        logging.error("header must be of type dict in get_product_page.")
        raise TypeError("header must be of type dict")
    if not url:
        logging.error("URL is empty")
        return None
    try:
        response = requests.get(url, headers=headers,
                                timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS)
        logging.info("get_product_page ran successfully.")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error("A request error has occurred: %s", e)
    except TimeoutError as e:
        logging.error("A timeout error has occurred: %s", e)
    return None


def get_soup(url: str, headers: dict) -> BeautifulSoup | None:
    """Returns a soup object for a game given the web address."""
    if not isinstance(url, str):
        logging.error("URL must be of type string in get_soup.")
        raise TypeError("URL must be of type string.")
    if not isinstance(headers, dict):
        logging.error("header must be of type string in get_soup.")
        raise TypeError("header must be of type dict")

    response = get_product_page(url, headers=headers)

    if response:
        logging.info("Get soup from product page response.")
        return BeautifulSoup(response, features="html.parser")
    logging.error("Failed to get a response from the URL")
    return None

def get_ses_client(config: _Environ) -> ses_client:
    """Returns an ses client from a configuration."""
    return boto_client(
        "ses",
        aws_access_key_id = config["ACCESS_KEY"],
        aws_secret_access_key = config["SECRET_ACCESS_KEY"],
        region_name = config["AWS_REGION_NAME"]
    )

def is_ses(boto_ses_client: ses_client) -> bool:
    """Returns true if ses client else false."""
    return (isinstance(boto_ses_client, BaseClient)
            and boto_ses_client._service_model.service_name == "ses")  # pylint: disable=protected-access

def can_parse_as_float(to_check: any) -> bool:
    """Determines if a value can be parsed as a float.
    Returns True on success, else False."""
    try:
        float(to_check)
        return True
    except (ValueError, TypeError):
        logging.error("Input can"t be parsed as a float")
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
    if user_id is None:
        return None
    return user_id.get("user_id")

def get_product_id(conn: connection, url: str) -> int | None:
    """Gets the products id from the database given a url."""
    with get_cursor(conn) as cur:
        cur.execute("SELECT product_id from products WHERE url = %s;", (url,))
        product_id = cur.fetchone()
    if product_id is None:
        return None
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
    if isinstance(price_threshold, (int, float)) and price_threshold <= 0:
        return False
    try:
        with get_cursor(conn) as cur:
            cur.execute("""INSERT INTO subscriptions
                         (user_id, product_id, price_threshold)
                        VALUES (%s, %s, %s);""", (user_id, product_id, price_threshold))
            conn.commit()
        return True
    except Exception:
        return False

def update_db_to_subscribe(
        conn: connection, product_url: str, price_threshold: bool | None, user_email: str) -> bool:
    """Inserts a subscription into a database, if it doesn"t already exist.
    Returns a dictionary, with the following attributes:
        `success`: bool = represents whether the database updated/contains subscription
        `message`: str  = contains a message signifying a message to display."""
    user_id = get_user_id(conn, user_email)
    if not user_id:
        logging.error("User not validated. Please try again!")
        return {"success": False, "message": "User not validated, please try again."}
    product_id = get_product_id(conn, product_url)
    if not product_id:
        logging.error("Unexpected error, please try again later.")
        return {"success": False, "message": "Unexpected error, please try again later."}
    if is_subscription_in_table(conn, user_id, product_id):
        logging.error("You are already subscribed to this product!")
        return {"success": True, "message": "You are already subscribed to this product!"}
    inserting_status = insert_subscription_into_db(conn, user_id, product_id, price_threshold)
    if inserting_status:
        logging.info("New subscription added!")
        return {"status": True, "message": "New subscription added."}
    logging.info("update_db_to_subscribe failed unexpectedly (insert_subscription_to_db).")
    return {"status": False, "message": "Unable to subscribe to product, please try again."}


def get_subscribed_products(conn: connection, email: str) -> list[dict]:
    """Get a list of all products subscribed by user, email."""
    with get_cursor(conn) as cur:
        cur.execute("""SELECT product_id, website_name, url, product_name, price_threshold
                    FROM websites
                    JOIN products USING (website_id)
                    JOIN subscriptions USING (product_id)
                    JOIN users USING (user_id)
                    WHERE email = %s""", (email,))
        subscribed_products = cur.fetchall()
    return subscribed_products

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

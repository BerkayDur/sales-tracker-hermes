"""This file contains functions that are used throughout this directory'''"""
from os import _Environ
import logging

import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
import requests
from bs4 import BeautifulSoup


DEFAULT_REQUEST_TIMEOUT_SECONDS = 30


def get_connection(config: _Environ) -> connection:
    """Establishes a connection with the database."""
    return psycopg2.connect(
        user=config["DB_USER"],
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        password=config["DB_PASSWORD"],
        port=config["DB_PORT"]
    )


def get_cursor(conn: connection) -> cursor:
    """Returns a cursor for the database."""
    if not isinstance(conn, connection):
        raise TypeError(
            'A cursor can only be constructed from a Psycopg2 connection object')
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def configure_logging() -> None:
    """Sets up basic logger"""
    return logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_product_page(url: str, headers: dict) -> str | None:
    """Fetch the HTML content of a product page from a given URL."""
    if not isinstance(url, str):
        raise TypeError('URL must be of type string.')
    if not isinstance(headers, dict):
        raise TypeError('header must be of type dict')

    if not url:
        logging.error("URL is empty")
        return None
    try:
        response = requests.get(url, headers=headers,
                                timeout=DEFAULT_REQUEST_TIMEOUT_SECONDS)
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error("A request error has occurred: %s", e)
    except TimeoutError as e:
        logging.error("A timeout error has occurred: %s", e)
    return None


def get_soup(url: str, headers: dict) -> BeautifulSoup | None:
    """Returns a soup object for a game given the web address."""
    if not isinstance(url, str):
        raise TypeError('URL must be of type string.')
    if not isinstance(headers, dict):
        raise TypeError('header must be of type dict')

    response = get_product_page(url, headers=headers)

    if response:
        return BeautifulSoup(response, features="html.parser")
    logging.error("Failed to get a response from the URL")
    return None

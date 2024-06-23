"""This file contains functions that are used throughout this directory'''"""
import logging

import requests
from bs4 import BeautifulSoup


DEFAULT_REQUEST_TIMEOUT_SECONDS = 30


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

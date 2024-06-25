"""This file contains functions that are used throughout this directory"""

import logging
import requests
from bs4 import BeautifulSoup

DEFAULT_REQUEST_TIMEOUT_SECONDS = 30


def configure_log() -> None:
    """Configures log output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def has_required_keys(entry, required_keys):
    """Check if all required keys are present in the dictionary."""
    return all(key in entry for key in required_keys)


def has_correct_types(entry, required_keys):
    """Check if all required keys have the correct data type."""
    return all(isinstance(entry[key], required_type)
               for key, required_type in required_keys.items())


def convert_product_code(entry: dict) -> bool:
    """Convert the product_code from str to int."""
    try:
        entry['product_code'] = int(entry['product_code'])
        return True
    except (ValueError, TypeError) as e:
        logging.error("Error has occured: %s", e)
        return False


def validate_input(entry):
    """Validates the input list of products"""
    required_keys = {
        'product_id': int,
        'url': str,
        'product_code': int,
        'product_name': str
    }

    if (isinstance(entry, dict) and has_required_keys(entry, required_keys) and
            convert_product_code(entry) and has_correct_types(entry, required_keys)):
        return entry
    logging.error("Entry is NOT valid")

    return None


def remove_stale_products(products: list[dict]) -> list[dict]:
    """remove products where the price hasn't decreased!"""
    return [product for product in products
            if product.get('previous_price') is None
            or product['current_price'] <= product['previous_price']]


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

"Extract Script: Pulls product information from ASOS webspage"
import json
import logging
from bs4 import BeautifulSoup
from utilities.helpers import get_soup, configure_logging


def is_correct_page(soup: BeautifulSoup) -> bool:
    """Returns True if asos product page, else False."""
    if not isinstance(soup, BeautifulSoup):
        raise TypeError('Soup must be of type BeautifulSoup')

    single_product_identifier = soup.find(
        'div', attrs={'class': 'single-product'})
    return single_product_identifier is not None


def scrape_product_information(soup: BeautifulSoup) -> dict | None:
    """Extract product information from a BeautifulSoup object."""
    if not isinstance(soup, BeautifulSoup):
        raise TypeError('Soup must be of type BeautifulSoup')

    product_soup = soup.find('script', type="application/ld+json")
    if product_soup:
        product_data = json.loads(product_soup.string)
        return product_data
    logging.error("Product information script not found in the page")
    return None


def get_product_code_asos(product_data: dict) -> str | None:
    """Returns product ID from the webpage"""
    if not isinstance(product_data, dict):
        raise TypeError('product_info must be of type dict')
    if not product_data:
        logging.error("Missing product data")
        return None

    product_id = product_data.get("productID")
    if product_id:
        return str(product_id)

    graph = product_data.get("@graph")
    if graph:
        product_id = graph[0]['productID']
        return product_id

    logging.error("Missing productID in product_data")
    return None


def get_product_name_asos(product_data: dict) -> str | None:
    """Returns product ID from the webpage"""
    if not isinstance(product_data, dict):
        raise TypeError('product_info must be of type dict')

    if not product_data:
        logging.error("Missing product data")
        return None

    product_name = product_data.get("name")
    if product_name:
        return product_name

    graph = product_data.get("@graph")
    if graph:
        product_name = graph[0]['name']
        return product_name

    logging.error("Missing productID in product_data")
    return None


def extract_product_information(url: str) -> dict | None:
    """ Extracts product information from a specific URL."""
    configure_logging()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    logging.info("Extraction started")
    soup = get_soup(url, headers=headers)
    if not soup:
        logging.error("Failed to scrape website for unknown reason.")
        raise ValueError('Failed to scrape website for unknown reason.')

    if not is_correct_page(soup):
        logging.error('Website page is invalid, it must be a product page.')
        raise ValueError('Website page is invalid!')

    logging.info("Scraping web page")
    data = scrape_product_information(soup)
    if not data:
        logging.error("Unable to extract information from product page!")
        return None

    product_code = get_product_code_asos(data)
    product_name = get_product_name_asos(data)
    if not (product_code and product_name):
        logging.error(
            'Unable to get correct product code or product name from website!')
        return None
    logging.info("Extraction completed successfully!")
    return {
        'url': url,
        'product_code': product_code,
        'product_name': product_name
    }


if __name__ == "__main__":
    URL = "ENTER YOUR URL HERE"
    extract_product_information(URL)

"""Extract Script: Pulls current price and sale status from ASOS API"""

from datetime import datetime
import logging
from bs4 import BeautifulSoup
from bs4.element import Tag
import requests
import json

from helpers import get_soup


def get_asos_api_url(product_code: int) -> str | None:
    """Returns the API URL for a given product on the ASOS website."""
    if not isinstance(product_code, int):
        logging.error('Product ID must be a integer to get the url.')
        return None

    return f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        {product_code}&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"


def get_product_info(soup: BeautifulSoup) -> BeautifulSoup | None:
    """Extract product information from a BeautifulSoup object."""
    if not isinstance(soup, BeautifulSoup):
        logging.error("Soup must be of type BeautifulSoup")
        raise TypeError('Soup must be of type BeautifulSoup')
    product_soup = soup.find(
        'span', class_=['js-buy-config-price', 'buy-config-price'])
    if product_soup:
        return product_soup
    logging.error("Product information script not found in the page")
    return None


def get_current_price(product_info: BeautifulSoup) -> int | None:
    """Extracts the current price of the product from the product information."""
    if not isinstance(product_info, Tag):
        logging.error('product_info must be of type Tag')
        raise TypeError('product_info must be of type Tag')

    try:
        sales_price_span = product_info.find('span', class_='sales')

        value_span = sales_price_span.find('span', class_='value')

        price = int(value_span['content'])

        return price
    except KeyError as e:
        logging.error("Error getting current price %s:", e)
    return None


def get_sale_status(product_info: BeautifulSoup) -> bool | None:
    """Determines if the product is on sale based on its discount percentage."""
    if not isinstance(product_info, Tag):
        logging.error('product_info must be of type Tag')
        raise TypeError('product_info must be of type Tag')

    try:
        discount_span = product_info.find('span', class_='discount-percentage')

        if discount_span and discount_span.get_text(strip=True):
            return True
        return False

    except KeyError as e:
        logging.error("Error getting sale status:%s", e)
        return None


def is_correct_page(soup: BeautifulSoup) -> bool:
    """Returns True if patagonia product page, else False."""
    if not isinstance(soup, BeautifulSoup):
        logging.error("Soup must be of type BeautifulSoup")
        raise TypeError('Soup must be of type BeautifulSoup')

    single_product_identifier = soup.find(
        'div', attrs={'class': 'product-detail'})
    return single_product_identifier is not None


def process_product(product: dict) -> dict | None:
    """Populates a single product dictionary with current price, reading time, and sale status."""

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    logging.info("Extraction started")
    soup = get_soup(product["url"], headers=headers)
    if not soup:
        logging.error("Failed to scrape website for unknown reason.")
        raise ValueError('Failed to scrape website for unknown reason.')

    if not is_correct_page(soup):
        logging.error('Website page is invalid, it must be a product page.')
        raise ValueError('Website page is invalid!')

    product_info = get_product_info(soup)

    if product_info:
        curr_price = get_current_price(product_info)
        sale = get_sale_status(product_info)

        if not sale is None and not curr_price is None:
            product['current_price'] = curr_price
            product['is_on_sale'] = sale
            product['reading_at'] = datetime.now().isoformat(".", "seconds")
            return product
    logging.error("Error processing product %s", product['product_code'])
    return None

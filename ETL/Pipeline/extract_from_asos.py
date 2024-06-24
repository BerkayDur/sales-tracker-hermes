"""Extract Script: Pulls current price and sale status from ASOS API"""
from datetime import datetime
import logging

import requests


def get_asos_api_url(product_code: int) -> str | None:
    """Returns the API URL for a given product on the ASOS website."""
    if not isinstance(product_code, int):
        logging.error('Product ID must be a integer to get the url.')
        return None

    return f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        {product_code}&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"


def get_product_info(product_data: dict, headers: dict) -> dict | None:
    """Gets the price information for a specified product from the ASOS API."""
    if not isinstance(product_data, dict):
        raise TypeError('product_info must be of type dict')
    if not isinstance(headers, dict):
        raise TypeError('header must be of type dict')

    price_endpoint = get_asos_api_url(product_data['product_code'])

    if not price_endpoint:
        return None

    try:
        response = requests.get(price_endpoint, headers, timeout=40)
        response.raise_for_status()

    except requests.exceptions.Timeout as e:
        logging.error("Timeout occurred in get_product_info: %s", e)
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException occurred in get_product_info: %s", e)
        return None

    response_json = response.json()

    if 'errorCode' in response_json or response_json is None or len(response_json) == 0:
        logging.error('No valid ProductIds requested')
        return None

    return response_json[0]


def get_current_price(product_info: dict) -> int | None:
    """Extracts the current price of the product from the product information."""
    if not isinstance(product_info, dict):
        raise TypeError('product_info must be of type dict')

    try:
        return product_info["productPrice"]["current"]["value"]
    except KeyError as e:
        logging.error("Error getting current price %s:", e)
    return None


def get_sale_status(product_info: dict) -> bool | None:
    """Determines if the product is on sale based on its discount percentage."""
    if not isinstance(product_info, dict):
        raise TypeError('product_info must be of type dict')

    try:
        discount = product_info["productPrice"]["discountPercentage"]
        return discount > 0

    except KeyError as e:
        logging.error("Error getting sale status:%s", e)
        return None


def process_product(product: dict) -> dict | None:
    """Populates a single product dictionary with current price, reading time, and sale status."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    product_info = get_product_info(product, headers)

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


# if __name__ == '__main__':
#     print(handler(None, None))

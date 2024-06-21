"""Extract Script: Pulls current price and sale status from ASOS API"""
from datetime import datetime
import logging

import requests
from lambda_multiprocessing import Pool


def configure_log() -> None:
    """Configures log output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_url(product_code: int) -> str | None:
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

    price_endpoint = get_url(product_data['product_code'])

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

    if 'errorCode' in response_json or response_json is None:
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


def extract_price_and_sales_data(product_list: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time,
    and sale status using multiprocessing."""
    logging.info("Starting Extraction")
    with Pool(processes=4) as pool:
        logging.info("Adding the current price and sale status")
        results = list(pool.map(process_product, product_list))
        logging.info("Finished Extraction")
        logging.info("Removing erroneous / missing data")
        results = [i for i in results if i is not None]
    return [results]


def has_required_keys(entry, required_keys):
    """Check if all required keys are present in the dictionary."""
    return all(key in entry for key in required_keys)


def is_dict(entry):
    """Check if the entry is a dictionary."""
    return isinstance(entry, dict)


def has_correct_types(entry, required_keys):
    """Check if all required keys have the correct data type."""
    return all(isinstance(entry[key], required_type)
               for key, required_type in required_keys.items())


def convert_product_code(entry):
    """Convert the product_code from str to int."""
    try:
        entry['product_code'] = int(entry['product_code'])
        return True
    except (ValueError, TypeError):
        return False


def validate_input(product_list):
    """Validates the input list of products"""
    required_keys = {
        'product_id': int,
        'url': str,
        'product_code': int,
        'product_name': str
    }
    valid_entries = []

    for entry in product_list:
        if (is_dict(entry) and has_required_keys(entry, required_keys) and
                convert_product_code(entry) and has_correct_types(entry, required_keys)):
            valid_entries.append(entry)

    if not valid_entries:
        raise ValueError(
            "The list is empty after validation. Please provide a valid product list.")

    return valid_entries


def handler(_event, _context=None) -> dict:
    """Main function which lambda will call"""
    configure_log()
    cleaned_data = validate_input(_event["output"])
    product_readings = extract_price_and_sales_data(cleaned_data)
    return {"output": product_readings}


if __name__ == '__main__':
    print(handler(None, None))

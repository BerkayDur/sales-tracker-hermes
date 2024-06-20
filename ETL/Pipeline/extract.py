"Extract Script: Pulls current price and sale status from ASOS API"
from datetime import datetime
import requests
from lambda_multiprocessing import Pool


def get_url(product_id: int) -> str:
    """Returns the API URL for a given product on the ASOS website."""
    if not isinstance(product_id, int):
        raise TypeError('Product id must be a integer to get the url.')

    return f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        {product_id}&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"


def get_product_info(product_data: int, headers: dict) -> int:
    """Gets the price information for a specified product from the ASOS API."""
    price_endpoint = get_url(product_data['product_id'])

    response = requests.get(price_endpoint, headers, timeout=60)

    if 'errorCode' in response:
        raise ValueError(f"API error: {response['errorMessage']}")
    return response.json()[0]


def get_current_price(product_info: dict) -> int:
    """Extracts the current price of the product from the product information."""
    try:
        return product_info["productPrice"]["current"]["value"]
    except KeyError as e:
        return f"Error getting current price: {e}"


def get_sale_status(product_info: dict) -> bool:
    """Determines if the product is on sale based on its discount percentage."""
    try:
        discount = product_info["productPrice"]["discountPercentage"]
        return discount > 0
    except KeyError as e:
        return f"Error getting sale status: {e}"


def process_product(product: dict) -> dict:
    """Populates a single product dictionary with current price, reading time, and sale status."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    product_info = get_product_info(product, headers)
    product['current_price'] = get_current_price(product_info)
    product['reading_at'] = datetime.now()
    product['is_on_sale'] = get_sale_status(product_info)
    return product


def populate(product_list: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time, 
    and sale status using multiprocessing."""
    with Pool(processes=4) as pool:
        results = list(pool.map(process_product, product_list))
    return results

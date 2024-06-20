"""Extract Script: Pulls current price and sale status from ASOS API"""
from datetime import datetime
import requests
from lambda_multiprocessing import Pool
import logging


def get_url(product_id: int) -> str:
    """Returns the API URL for a given product on the ASOS website."""
    if not isinstance(product_id, int):
        logging.error('Product ID must be a integer to get the url.')
        return None

    return f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        {product_id}&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"


def get_product_info(product_data: int, headers: dict) -> int:
    """Gets the price information for a specified product from the ASOS API."""
    price_endpoint = get_url(product_data['product_id'])

    if not price_endpoint:
        return None

    response = requests.get(price_endpoint, headers, timeout=60).json()

    if 'errorCode' in response or not response:
        logging.error('No valid ProductIds requested')
        return None

    return response[0]


def get_current_price(product_info: dict) -> int:
    """Extracts the current price of the product from the product information."""
    try:
        return product_info["productPrice"]["current"]["value"]
    except KeyError as e:
        logging.error(f"Error getting current price:")
    return None


def get_sale_status(product_info: dict) -> bool:
    """Determines if the product is on sale based on its discount percentage."""
    try:
        discount = product_info["productPrice"]["discountPercentage"]
        return discount > 0
    except KeyError as e:
        logging.error(f"Error getting sale status: {e}")
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
            product['reading_at'] = datetime.now()
            return product
    return None


def populate(product_list: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time, 
    and sale status using multiprocessing."""
    logging.info("Starting Extraction")
    with Pool(processes=4) as pool:
        logging.info("Adding the current price and sale status")
        results = list(pool.map(process_product, product_list))
        results = list(filter(lambda x: x != None, results))

    return results


def configure_log() -> None:
    """Configures log output"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


if __name__ == '__main__':
    inputs = [{
        'product_id': 2,
        'current_price': '',
        'previous_price': 85,
        'url': "https://www.asos.com/adidas-originals/adidas-originals-gazelle-trainers-in-white-and-blue/prd/205759745#ctaref-we%20recommend%20carousel_11&featureref1-we%20recommend%20pers",
        'product_name': 'adidas Originals Gazelle trainers in white and blue White'
    },
        {
        'product_id': 206107351,
        'current_price': '',
        'previous_price': 56,
        'url': "https://www.asos.com/new-balance/new-balance-fresh-foam-arishi-v4-running-trainers-in-white-and-orange/prd/206107351#colourWayId-206107353",
        'product_name': 'New Balance Fresh Foam Arishi v4 running trainers in white and orange'
    },

        {
        'product_id': 205928631,
        'current_price': '',
        'previous_price': 25,
        'url': "https://www.asos.com/pasq/pasq-two-pocket-tote-bag-with-removable-pouch-in-black/prd/205928631#colourWayId-205928635",
        'product_name': 'PASQ two pocket tote bag with removable pouch in black'
    }]
    configure_log()
    print(populate(inputs))

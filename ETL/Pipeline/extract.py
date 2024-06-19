from datetime import datetime
import requests
from lambda_multiprocessing import Pool


inputs = [{
    'product_id': 205759745,
    'current_price': '',
    'previous_price': 85,
    'url': "https://www.asos.com/adidas-originals/adidas-originals-gazelle-trainers-in-white-and-blue/prd/205759745#ctaref-we%20recommend%20carousel_11&featureref1-we%20recommend%20pers",
    'product_name': 'adidas Originals Gazelle trainers in white and blue White'
}, {
    'product_id': 206059258,
    'current_price': '',
    'previous_price': 100,
    'url': "https://www.asos.com/adidas-originals/adidas-originals-samba-lt-trainers-in-yellow-and-green/prd/206059258#ctaref-we%20recommend%20carousel_12&featureref1-we%20recommend%20pers",
    'product_name': 'adidas Originals Samba LT trainers in yellow and green'
}
]


def get_product_info(product_data: int, headers: dict) -> int:
    """Gets the price information for a specified product from the ASOS API."""
    price_endpoint = f"https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        {product_data['product_id']}&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"
    response = requests.get(price_endpoint, headers=headers).json()[0]

    if 'errorCode' in response:
        raise ValueError(f"API error: {response['errorMessage']}")
    return response


def get_current_price(product_info: dict) -> int:
    """Extracts the current price of the product from the product information."""
    try:
        return product_info["productPrice"]["current"]["value"]
    except KeyError as e:
        raise RuntimeError(f"Error getting current price: {e}")


def get_sale_status(product_info: dict) -> bool:
    """Determines if the product is on sale based on its discount percentage."""
    try:
        discount = product_info["productPrice"]["discountPercentage"]
        return discount > 0
    except KeyError as e:
        raise RuntimeError(f"Error getting current price: {e}")


def process_product(product: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time, and sale status."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
    product_info = get_product_info(product, headers)
    product['current_price'] = get_current_price(product_info)
    product['reading_at'] = datetime.now()
    product['is_on_sale'] = get_sale_status(product_info)
    return product


def populate_dict(product_list: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time, and sale status using multiprocessing."""
    with Pool(processes=4) as pool:
        results = list(pool.map(process_product, product_list))
    return results


if __name__ == "__main__":
    print(populate_dict(inputs))

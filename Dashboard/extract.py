"Extract Script: Pulls product information from ASOS webspage"
import json
import logging
import requests
from bs4 import BeautifulSoup

DEFAULT_REQUEST_TIMEOUT_SECONDS = 30


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
    response = get_product_page(url, headers=headers)

    if response:
        return BeautifulSoup(response, features="html.parser")
    logging.error("Failed to get a response from the URL")
    return None


def scrape_product_information(soup: BeautifulSoup) -> dict | None:
    """Extract product information from a BeautifulSoup object."""
    if not soup:
        logging.error("Soup object is None")
        return None

    product_soup = soup.find('script', type="application/ld+json")
    if product_soup:
        product_data = json.loads(product_soup.string)
        return product_data
    logging.error("Product information script not found in the page")
    return None


def get_product_code(product_data: dict) -> str | None:
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


def get_product_name(product_data: dict) -> str | None:
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


def configure_logging() -> None:
    """Sets up basic logger"""
    return logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def extract_product_information() -> tuple | None:
    """ Extracts product information from a specific URL."""
    configure_logging()
    url = "https://www.asos.com/asos-design/asos-design-disney-oversized-unisex-tee-in-off-white-with-mickey-mouse-graphic-prints/prd/205987755#colourWayId-205987756"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    logging.info("Extraction started")
    soup = get_soup(url, headers=headers)
    if not soup:
        logging.error("Failed to scrape product information")
        return None

    logging.info("Scraping web page")
    data = scrape_product_information(soup)
    if data:
        product_code = get_product_code(data)
        product_name = get_product_name(data)
        logging.info("Extraction completed successfully!")
        return (url, product_code, product_name)

    logging.error("Extraction failed!")
    return None


if __name__ == "__main__":
    extract_product_information()

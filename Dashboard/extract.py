import json
import requests
from bs4 import BeautifulSoup
import logging


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}


def get_product_page(url: str, headers: dict) -> str:
    """Fetch the HTML content of a product page from a given URL."""
    if not url:
        logging.error("URL is empty")
        return None
    try:
        response = requests.get(url, headers=headers)
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error("A request error has occurred: %s", e)
    except TimeoutError as e:
        logging.error("A timeout error has occurred: %s", e)
    return None


def get_soup(url: str, headers: dict) -> BeautifulSoup:
    """Returns a soup object for a game given the web address."""
    response = get_product_page(url, headers=headers)
    if response:
        return BeautifulSoup(response, features="html.parser")
    logging.error("Failed to get a response from the URL")
    return None


def scrap_product_information(soup: BeautifulSoup) -> dict:
    if not soup:
        logging.error("Soup object is None")
        return None

    product_soup = soup.find('script', type="application/ld+json")
    if product_soup:
        product_data = json.loads(product_soup.string)
        return product_data
    logging.error("Product information script not found in the page")
    return None


def get_product_code(product_data: dict) -> str:
    """Returns product ID from the webpage"""
    if not product_data or 'productID' not in product_data:
        logging.error("Missing productID")
        return None
    return product_data["productID"]


def get_product_name(product_data: dict) -> str:
    """Returns product name from the webpage"""
    if not product_data or 'name' not in product_data:
        logging.error("Missing product name")
        return None
    return product_data["name"]


def configure_logging():
    return logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def extract_product_information():
    configure_logging()
    url = "https://www.asos.com/adidas-originals/adidas-originals-gazelle-trainers-in-white-and-blue/prd/205759745#ctaref-we%20recommend%20carousel_11&featureref1-we%20recommend%20pers"
    # url = ""

    logging.info("Extraction started")
    soup = get_soup(url, headers=HEADERS)
    if not soup:
        logging.error("Failed to scrap product information")

    logging.info("Scraping web page")
    data = scrap_product_information(soup)
    if data:
        product_code = get_product_code(data)
        product_name = get_product_name(data)
        logging.info("Extraction completed successfully!")
        return (product_code, product_name)
    else:
        logging.error("Failed to scrap product information")


if __name__ == "__main__":
    extract_product_information()
    # print(get_product_page("", headers=HEADERS))

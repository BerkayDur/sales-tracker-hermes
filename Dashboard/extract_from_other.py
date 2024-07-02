"Extract Script: Pulls product information from unrecognised webpages"

import json
import logging
from os import _Environ, environ as ENV

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from scrapegraphai.graphs import SmartScraperGraph

from helpers import get_product_page, configure_logging


def scrape_product_information(html: str, config: _Environ) -> dict | None:
    """Extract product information from an html str object."""
    if not isinstance(html, str):
        logging.error("html must be of type str")
        raise TypeError("html must be of type str")

    openai_key = config.get("OPENAI_KEY")

    smart_scraper_graph = SmartScraperGraph(
        prompt="""
        You are provided with an HTML document containing information about a product.
        Your task is to extract only the product name and product code.
        Output the result in the following json format:
        {'product_name': 'name', 'product_code': 'code'}.
        Do not include any other information.
        If unable to find, return 'NA' in the value.
        """,
        source=html,
        config={
            "llm": {
                "api_key": openai_key,
                "model": "gpt-3.5-turbo",
            },
            "embeddings": {
                "model": "ollama/nomic-embed-text",
                "temperature": 0,
                "base_url": "http://localhost:11434",
            }
        }
    )

    product_data = smart_scraper_graph.run()

    if (product_data and
        product_data.get("product_name") and
        product_data.get("product_code") and
        product_data["product_name"] != "NA" and
            product_data["product_code"] != "NA"):
        logging.info("Scraping completed successfully!")
        return product_data
    logging.error("Failed to scrape from the webpage")
    return None


def extract_product_information(url: str) -> dict | None:
    """ Extracts product information from a specific URL."""
    configure_logging()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    logging.info("Extraction started")
    page_html = get_product_page(url, headers=headers)
    if not page_html:
        logging.error("Failed to scrape website for unknown reason.")
        raise ValueError("Failed to scrape website for unknown reason.")

    logging.info("Scraping web page")
    data = scrape_product_information(page_html, ENV)
    if not data:
        logging.error("Unable to extract information from product page!")
        return None

    product_code = data["product_code"]
    product_name = data["product_name"]
    if not (product_code and product_name):
        logging.error(
            "Unable to get correct product code or product name from website!")
        return None
    logging.info("Extraction completed successfully!")

    return {
        "url": url,
        "product_code": product_code,
        "product_name": product_name
    }


if __name__ == "__main__":
    load_dotenv()
    # URL = "ENTER YOUR URL HERE"
    URL = "https://store.steampowered.com/app/990080/Hogwarts_Legacy/"
    print(extract_product_information(URL))

"""Extract Script: Pulls current price and sale status from ASOS API"""

from datetime import datetime
import logging
from os import _Environ, environ as ENV
from dotenv import load_dotenv

from pipeline_helpers import get_product_page
from scrapegraphai.graphs import SmartScraperGraph


def scrape_product_information(html: str, config: _Environ) -> dict | None:
    """Extract product information from an html str object."""
    if not isinstance(html, str):
        logging.error("html must be of type str")
        raise TypeError("html must be of type str")

    openai_key = config.get("OPENAI_KEY")

    smart_scraper_graph = SmartScraperGraph(
        prompt="""
        You are provided with an HTML document containing information about a product.
        Your task is to extract the price of the product and a boolean value indicating whether the product is on sale or not (True or False only).
        Output the result in the following json format:
        {'price': _, 'is_on_sale': True/False}.
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
            }
        }
    )

    product_data = smart_scraper_graph.run()

    if (product_data and
        product_data.get("price") and
        product_data.get("is_on_sale") and
            product_data["price"] != "NA"):
        logging.info("Scraping completed successfully!")
        return product_data
    logging.error("Failed to scrape from the webpage")
    return None


def process_product(product: dict) -> dict | None:
    load_dotenv()
    """Populates a single product dictionary with current price, reading time, and sale status."""

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)\
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}

    logging.info("Extraction started")
    page_html = get_product_page(product["url"], headers=headers)
    if not page_html:
        logging.error("Failed to scrape website for unknown reason.")
        raise ValueError("Failed to scrape website for unknown reason.")

    logging.info("Scraping web page")
    price_data = scrape_product_information(page_html, ENV)
    if not price_data:
        logging.error("Unable to extract information from product page!")
        return None

    print(price_data)

    if price_data:
        curr_price = price_data["price"]
        sale = price_data["is_on_sale"]

        if not curr_price is None:
            product["current_price"] = curr_price
            product["is_on_sale"] = sale
            product["reading_at"] = datetime.now().isoformat(".", "seconds")
            return product
    logging.error("Error processing product %s", product["product_code"])
    return None


if __name__ == "__main__":
    load_dotenv()

    print(process_product({
        "product_id": 1,
        "url": "https://store.steampowered.com/app/1144200/Ready_or_Not/",
        "product_code": 203474246,
        "product_name": "adidas Running Response trainers in white and blue",
        "website_name": "asos"
    }))

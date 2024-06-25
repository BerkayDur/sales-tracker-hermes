"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""
import logging

from lambda_multiprocessing import Pool

from pipeline_helpers import configure_log, validate_input, remove_stale_products
from extract_patagonia import process_product as extract_from_asos
from extract_patagonia import process_product as extract_from_patagonia


EXTRACT_FUNCTIONS = {
    'asos': extract_from_asos,
    'patagonia': extract_from_patagonia
}


def get_website_name(product_data: dict) -> str | None:
    """Returns the website from the product dictionary."""
    if not isinstance(product_data, dict):
        logging.error(
            'product_data must be of type dict')
        raise TypeError(
            'product_data must be of type dict')
    website_name = product_data.get('website_name')
    if website_name:
        return website_name
    logging.info('website name not found.')
    return None


def process(product_data: dict):
    """Processes product data by validating input, extracting the website name,
    and running the appropriate extraction function."""

    clean_data = validate_input(product_data)
    if not clean_data:
        logging.error("Data did not pass validation")
        return None
    website_name = get_website_name(clean_data)

    if not website_name:
        logging.error('No API found for %s', product_data['product_code'])
        return None
    logging.info('Starting to run %s extract script.', website_name)
    try:
        website_data = EXTRACT_FUNCTIONS[website_name](product_data)
        return website_data
    except ValueError:
        logging.error('extract from product %s failed! for %s ',
                      website_name, product_data['product_code'])
        return None


def extract_price_and_sales_data(product_list: list[dict]) -> list[dict]:
    """Populates each product dictionary in the product list with current price, reading time,
    and sale status using multiprocessing."""
    logging.info("Starting Extraction")
    with Pool(processes=4) as pool:
        logging.info("Adding the current price and sale status")
        results = list(pool.map(process, product_list))
        logging.info("Finished Extraction. Removing erroneous / missing data")
        results = [i for i in results if i is not None]
    return results


def handler(_event, _context=None) -> list:
    """Main function which lambda will call"""
    configure_log()
    product_readings = extract_price_and_sales_data(_event)
    return remove_stale_products(product_readings)


if __name__ == "__main__":
    configure_log()
    # cleaned_data = _event
    # product_readings = extract_price_and_sales_data(cleaned_data)
    # print(remove_stale_products(product_readings))
    for i in handler([
              {
        "product_id": 1,
        "product_code": "23725",
        "url": "https://eu.patagonia.com/gb/en/product/womens-capilene-cool-trail-graphic-shirt/23725.html?dwvar_23725_color=FMWI&cgid=collections-new-arrivals",
        "price": None,
        "website_name": "patagonia",
        "product_name": "W's Capilene® Cool Trail Graphic Shirt"
      }
    ]):
        print(i)
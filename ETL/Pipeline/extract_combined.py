"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""
import logging

from lambda_multiprocessing import Pool

from helpers import configure_log, validate_input, remove_stale_products
from extract_from_asos import process_product as extract_from_asos


EXTRACT_FUNCTIONS = {
    'asos': extract_from_asos
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
    cleaned_data = validate_input(_event)
    product_readings = extract_price_and_sales_data(cleaned_data)
    return remove_stale_products(product_readings)


if __name__ == '__main__':
    configure_log()
    inputs = [
        {
            'product_id': 1,
            'url': "https://www.asos.com/bershka/bershka-high-waisted-bootcut-jeans\
-in-black/prd/203832070#colourWayId-203832078",
            'product_code': 203832070,
            'product_name': 'Bershka high waisted bootcut jeans in black',
            'website_name': 'asos'
        },
        {
            'product_id': 2,
            'product_code': 206107351,
            'url': "https://www.asos.com/new-balance/new-balance-fresh-foam-arishi-v4\
        -running-trainers-in-white-and-orange/prd/206107351#colourWayId-206107353",
            'product_name': 'New Balance Fresh Foam Arishi v4 running trainers in white and orange',
            'website_name': 'asos'
        },
        {
            'product_id': 3,
            'product_code': 205918844,
            'url': "https://www.asos.com/pasq/pasq-two-pocket-tote-bag-\
        with-removable-pouch-in-black/prd/205928631#colourWayId-205928635",
            'product_name': 'PASQ two pocket tote bag with removable pouch in black',
            'website_name': 'asos'
        }
    ]

    print(extract_price_and_sales_data(inputs))

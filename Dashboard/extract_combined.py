"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""

import re

from extract_from_asos import extract_product_information as extract_from_asos


EXTRACT_FUNCTIONS = {
    'asos' : extract_from_asos
}

def identify_store(product_url: str) -> str | None:
    """Returns the store from the given URL."""
    if not isinstance(product_url, str):
        raise TypeError('product_url passed to identify_store must be of type str')
    for store_name in EXTRACT_FUNCTIONS.keys():
        if store_name in product_url:
            return store_name
    return None



def extract_product_information(product_url: str) -> tuple:
    """Given an URL identifies the store and calls the relevant extract file."""
    store_name = identify_store(product_url)

    if store_name:
        if store_name.lower() in EXTRACT_FUNCTIONS:
            
        else:
            print(f"Extraction module for '{store_name}' not found.")
    else:
        print("Store not identified.")


if __name__ == '__main__':
    URL = "https://www.asos.com/asos-design/asos-design-disney-oversized-\
unisex-tee-in-off-white-with-mickey-mouse-graphic-prints/prd/205987755#colourWayId-205987756"
    extract_product_information(URL)

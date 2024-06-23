"""Combined Extract Script: Identifies the store name and executes the relevant extraction"""
import importlib
import re


STORE_LIST = ['asos']


def identify_store(product_url: str) -> str | None:
    """Returns the store from the given URL."""
    store_patterns = {
        r'^(https?://)?(www\.)?asos\.[a-zA-Z]{2,}/.*': 'Asos'}

    for pattern, store_name in store_patterns.items():
        if re.match(pattern, product_url):
            return store_name

    print("Store not identified")
    return None


def extract_product_information(product_url: str) -> tuple:
    """Given an URL identifies the store and calls the relevant extract file."""
    store_name = identify_store(product_url)

    if store_name:
        if store_name.lower() in STORE_LIST:
            filename = f"extract_from_{store_name.lower()}"
            try:

                spec = importlib.util.spec_from_file_location(
                    filename, f"{filename}.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(module.extract_product_information(product_url))
            except FileNotFoundError:
                print(f"Extraction module '{filename}.py' not found.")
            except AttributeError:
                print(
                    f"Module '{filename}' does not have 'extract_product_information' function.")
        else:
            print(f"Extraction module for '{store_name}' not found.")
    else:
        print("Store not identified.")


if __name__ == '__main__':
    URL = "https://www.asos.com/asos-design/asos-design-disney-oversized-\
unisex-tee-in-off-white-with-mickey-mouse-graphic-prints/prd/205987755#colourWayId-205987756"
    extract_product_information(URL)

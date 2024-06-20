"""Hold all the fixtures used in the test files"""

import pytest


@pytest.fixture(name="unsubscribed_products")
def fixture_unsubscribed_products() -> list[dict]:
    """Example data for unsubscribed products"""
    return [{"product_id": 4, "url": "http://example.com/product4",
             "product_code": "P004", "product_name": "Product 4"},
            {"product_id": 5, "url": "http://example.com/product5",
             "product_code": "P005", "product_name": "Product 5"}]

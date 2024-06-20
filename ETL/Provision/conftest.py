import pytest


@pytest.fixture(name="fake_readings")
def fixture_fake_readings():
    "Fake data for the database reading"
    return [{"product_id": 1, "url": "http://example.com/product1", "price": 19.99},
            {"product_id": 2, "url": "http://example.com/product2", "price": 24.99},
            {"product_id": 3, "url": "http://example.com/product3", "price": 12.34},
            {"product_id": 4, "url": "http://example.com/product4", "price": 228.99}]

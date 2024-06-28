"""Contains all the fixtures used in the test extract file"""

import pytest


@pytest.fixture(name="fake_headers")
def fixture_fake_headers() -> dict:
    """Example data for headers"""
    return {'User-Agent': 'test'}


@pytest.fixture(name="fake_product_data")
def fixture_fake_product_data() -> dict:
    """Example data for a product"""
    return {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': 12345,
        'product_name': 'adidas  trainers',
        'website_name': 'asos'
    }


@pytest.fixture(name="fake_product_list")
def fixture_fake_product_list() -> list[dict]:
    """Example data of a list of products"""
    return [
        {
            'product_id': 1,
            'url': "https://www.asos.com/bershka/bershka-high-waisted-bootcut-jeans\
-in-black/prd/203832070#colourWayId-203832078",
            'product_code': 203832070,
            'product_name': 'Bershka high waisted bootcut jeans in black'
        },
        {
            'product_id': 2,
            'product_code': 206107351,
            'url': "https://www.asos.com/new-balance/new-balance-fresh-foam-arishi-v4\
-running-trainers-in-white-and-orange/prd/206107351#colourWayId-206107353",
            'product_name': 'New Balance Fresh Foam Arishi v4 running trainers in white and orange'
        },
        {
            'product_id': 3,
            'product_code': "hh",
            'url': "https://www.asos.com/pasq/pasq-two-pocket-tote-bag-\
with-removable-pouch-in-black/prd/205928631#colourWayId-205928635",
            'product_name': 'PASQ two pocket tote bag with removable pouch in black'
        }
    ]


@pytest.fixture(name="fake_product_response_info")
def fixture_fake_product_response_info() -> dict:
    """Example data of a API response"""
    return {"productPrice": {
            "current": {"value": 70},
            "discountPercentage": 35}}


@pytest.fixture(name="required_keys")
def fixture_required_keys() -> list:
    """Example list of the required keys"""
    return ['product_id', 'url', 'product_code', 'product_name']


@pytest.fixture(name="required_data_types")
def fixture_required_data_types():
    """Example list of the required data types"""
    return {
        'product_id': int,
        'url': str,
        'product_code': int,
        'product_name': str
    }


@pytest.fixture(name="fake_url")
def fixture_fake_url() -> str:
    """Example data for product url"""
    return "www.asos.com/trainers"

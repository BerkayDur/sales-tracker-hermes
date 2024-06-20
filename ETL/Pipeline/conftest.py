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
        "product_id": 12345,
        "previous_price": 100,
        "url": "www.asos.com/shoes",
        "product_name": "adidas Originals Samba LT trainers"}


@pytest.fixture(name="fake_product_list")
def fixture_fake_product_list() -> list[dict]:
    """Example data of a list of products"""
    return [{
        'product_id': 205759745,
        'current_price': '',
        'previous_price': 85,
        'url': "https://www.asos.com/adidas-originals/adidas-originals-gazelle-trainers-in-\
            white-and-blue/prd/205759745#ctaref-we%20recommend%20carousel_11&featureref1-we%20recommend%20pers",
        'product_name': 'adidas Originals Gazelle trainers in white and blue White'
    }, {
        'product_id': 206059258,
        'current_price': '',
        'previous_price': 100,
        'url': "https://www.asos.com/adidas-originals/adidas-originals-samba-lt-trainers-in-yellow\
            -and-green/prd/206059258#ctaref-we%20recommend%20carousel_12&featureref1-we%20recommend%20pers",
        'product_name': 'adidas Originals Samba LT trainers in yellow and green'
    }
    ]


@pytest.fixture(name="fake_product_response_info")
def fixture_fake_product_response_info() -> dict:
    """Example data of a API response"""
    return {"productPrice": {
            "current": {"value": 70},
            "discountPercentage": 35}}

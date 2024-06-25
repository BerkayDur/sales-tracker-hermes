"""This file tests whether the extract_from_asos file works as expected"""

from unittest.mock import patch
import requests

import pytest

from extract_asos import (get_product_info, get_asos_api_url, get_current_price,
                               get_sale_status, process_product)


def test_get_asos_api_url_product_code(fake_product_data):
    """Tests the get_url function with a valid product code"""
    excepted_url = "https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        12345&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"
    assert get_asos_api_url(fake_product_data['product_code']) == excepted_url


@pytest.mark.parametrize("product_code", ['not_an_integer', None, 12.34, [1, 2, 3], {}])
def test_get_asos_api_url_non_integer_product_code(product_code):
    """Tests the get_url function with non integer values"""
    assert get_asos_api_url(product_code) is None


@patch('extract_asos.requests.get')
def test_get_product_info_success(mock_get, fake_product_data, fake_headers,
                                  fake_product_response_info):
    """Tests the get_product_info function passes with valid data"""

    mock_get.return_value.json.return_value = [fake_product_response_info]

    result = get_product_info(fake_product_data, fake_headers)
    assert result == fake_product_response_info
    assert mock_get.call_count == 1
    assert mock_get.call_args[1] == {'timeout': 40}


@patch('extract_asos.requests.get')
def test_get_product_info_timeout_exception(mock_get, fake_product_data, fake_headers):
    """Tests the get_product_info function raises a Timeout error"""

    mock_get.side_effect = requests.exceptions.Timeout
    product_info = get_product_info(fake_product_data, fake_headers)

    assert product_info is None


@patch('extract_asos.requests.get')
def test_get_product_info_request_exception(mock_get, fake_product_data, fake_headers):
    """Tests the get_product_info function raises a RequestsException error"""

    mock_get.side_effect = requests.exceptions.RequestException
    product_info = get_product_info(fake_product_data, fake_headers)

    assert product_info is None


@pytest.mark.parametrize("product_data", ['invalid', None, 12.34, [1, 2, 3], (11, 22)])
def test_get_product_info_invalid_product_data_type(fake_headers, product_data):
    """Tests get_product_info with invalid product data type"""
    with pytest.raises(TypeError):
        get_product_info(product_data, fake_headers)


@pytest.mark.parametrize("headers", ['invalid', None, 12.34, [1, 2, 3], 1])
def test_get_product_info_invalid_headers_type(fake_product_data, headers):
    """Tests get_product_info with invalid headers data type"""

    with pytest.raises(TypeError):
        get_product_info(fake_product_data, headers)


def test_get_current_price_valid_product_info(fake_product_response_info):
    """Tests the get_current_price function with valid data"""
    assert get_current_price(fake_product_response_info) == 70


def test_get_current_price_missing_data():
    """Tests the get_current_price function with a missing key"""
    product_info_missing_key = {}
    assert get_current_price(product_info_missing_key) is None


@pytest.mark.parametrize("product_info", ['invalid', None, 12.34, [1, 2, 3], (11, 22)])
def test_get_current_price_invalid_product_info_type(product_info):
    """Tests the get_current_price function with invalid data"""
    with pytest.raises(TypeError):
        get_current_price(product_info)


def test_get_sale_status_with_discount(fake_product_response_info):
    """Tests the get_sale_status function with valid data"""
    assert get_sale_status(fake_product_response_info)


def test_get_sale_status_failed():
    """Tests the get_sale_status function with a missing key"""
    product_info_missing_key = {}
    assert get_sale_status(product_info_missing_key) is None


def test_get_sale_status_no_discount():
    """Tests the get_sale_status function with no discount"""
    product_info_no_discount = {
        "productPrice": {
            "discountPercentage": 0
        }
    }
    assert not get_sale_status(product_info_no_discount)


@pytest.mark.parametrize("product_info", ['invalid', None, 12.34, [1, 2, 3], (11, 22)])
def test_get_sale_status_invalid_product_info_type(product_info):
    """Tests the function get_sale_status with incorrect data type for product info"""
    with pytest.raises(TypeError):
        get_sale_status(product_info)


@patch('extract_asos.requests.get')
def test_process_product(mock_get, fake_product_data, fake_product_response_info):
    """Tests the process_product function"""
    mock_get.return_value.json.return_value = [fake_product_response_info]
    processed_product = process_product(fake_product_data)
    assert processed_product['current_price'] == 70
    assert 'reading_at' in processed_product
    assert processed_product['is_on_sale']

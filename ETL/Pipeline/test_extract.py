"""This file tests whether the extract file works as expected"""
from unittest.mock import patch
import pytest

from extract import (get_product_info, get_url, get_current_price,
                     get_sale_status, process_product, populate)


def test_get_url_success(fake_product_data):
    """Tests the get_url function"""
    excepted_url = "https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        12345&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"
    assert get_url(fake_product_data['product_id']) == excepted_url


def test_get_url_fail():
    """Tests the get_url raises an error with an non int value"""
    assert get_url([1, 2, 3, 4]) is None


@patch('extract.requests.get')
def test_get_product_info_success(mock_get, fake_product_data, fake_headers,
                                  fake_product_response_info):
    """Tests the get_product_info function passes with valid data"""

    mock_get.return_value.json.return_value = [fake_product_response_info]

    result = get_product_info(fake_product_data, fake_headers)
    assert result == fake_product_response_info
    assert mock_get.call_count == 1
    assert mock_get.call_args[1] == {'timeout': 60}


@patch('extract.requests.get')
def test_get_product_info_failed(mock_get, fake_product_data, fake_headers):
    """Tests the get_product_info function fails with an empty response"""

    mock_get.return_value.json.return_value = []

    result = get_product_info(fake_product_data, fake_headers)
    assert result == None


@patch('extract.requests.get')
def test_get_product_info_empty_response(mock_get, fake_product_data, fake_headers):
    """Tests the get_product_info function fails with invalid data """

    mock_get.side_effect = ValueError("API error:")

    with pytest.raises(ValueError):
        result = get_product_info(fake_product_data, fake_headers)
        assert "API error" in result


def test_get_current_price_success(fake_product_response_info):
    """Tests the get_current_price function with valid data"""
    assert get_current_price(fake_product_response_info) == 70


def test_get_current_price_failed():
    """Tests the get_current_price function with a missing key"""
    product_info_missing_key = {}
    assert get_current_price(product_info_missing_key) is None


def test_get_sale_status_success(fake_product_response_info):
    """Tests the get_sale_status function with valid data"""
    assert get_sale_status(fake_product_response_info) is True


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
    assert get_sale_status(product_info_no_discount) is False


@patch('extract.process_product')
@patch('extract.Pool')
def test_populate_success(mock_Pool, mock_process_product, fake_product_list):
    """Tests the populate function"""
    populate(fake_product_list)
    assert mock_Pool.return_value.__enter__.return_value.map.call_count == 1
    assert mock_Pool.return_value.__enter__.return_value.map.call_args[
        0][0] == mock_process_product
    assert mock_Pool.return_value.__enter__.return_value.map.call_args[
        0][1] == fake_product_list


@patch('extract.requests.get')
def test_process_product(mock_get, fake_product_data, fake_product_response_info):
    """Tests the process_product function"""
    mock_get.return_value.json.return_value = [fake_product_response_info]
    processed_product = process_product(fake_product_data)
    assert processed_product['current_price'] == 70
    assert 'reading_at' in processed_product
    assert processed_product['is_on_sale'] is True

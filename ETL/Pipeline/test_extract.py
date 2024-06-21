"""This file tests whether the extract file works as expected"""
from unittest.mock import patch
import requests

import pytest

from extract import (get_product_info, get_url, get_current_price,
                     get_sale_status, process_product,
                     extract_price_and_sales_data, has_required_keys, is_dict,
                     has_correct_types, validate_input)


def test_get_url_valid_product_code(fake_product_data):
    """Tests the get_url function with a valid product code"""
    excepted_url = "https://www.asos.com/api/product/catalogue/v4/stockprice?productIds=\
        12345&store=COM&currency=GBP&keyStoreDataversion=ornjx7v-36&country=GB"
    assert get_url(fake_product_data['product_code']) == excepted_url


@pytest.mark.parametrize("product_code", ['not_an_integer', None, 12.34, [1, 2, 3], {}])
def test_get_url_non_integer_product_code(product_code):
    """Tests the get_url function with non integer values"""
    assert get_url(product_code) is None


@patch('extract.requests.get')
def test_get_product_info_success(mock_get, fake_product_data, fake_headers,
                                  fake_product_response_info):
    """Tests the get_product_info function passes with valid data"""

    mock_get.return_value.json.return_value = [fake_product_response_info]

    result = get_product_info(fake_product_data, fake_headers)
    assert result == fake_product_response_info
    assert mock_get.call_count == 1
    assert mock_get.call_args[1] == {'timeout': 40}


@patch('extract.requests.get')
def test_get_product_info_timeout_exception(mock_get, fake_product_data, fake_headers):
    """Tests the get_product_info function raises a Timeout error"""

    mock_get.side_effect = requests.exceptions.Timeout
    product_info = get_product_info(fake_product_data, fake_headers)

    assert product_info is None


@patch('extract.requests.get')
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


@patch('extract.process_product')
@patch('extract.Pool')
def test_extract_price_and_sales_data_success(mock_Pool, mock_process_product, fake_product_list):
    """Tests the populate function"""
    extract_price_and_sales_data(fake_product_list)
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
    assert processed_product['is_on_sale']


@patch('extract.get_product_info', return_value=None)
def test_process_product_get_product_info_none(mock_get_product_info, fake_product_data):
    """Test the process product function with a none value"""
    processed_product = process_product(fake_product_data)

    assert processed_product is None
    mock_get_product_info.assert_called_once()


def test_has_required_keys_all_keys_present(required_keys, fake_product_data):
    """Test the has all keys function with valid data"""
    assert has_required_keys(fake_product_data, required_keys)


def test_has_required_keys_missing_keys(required_keys):
    """Test the has all keys function with missing keys"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': 12345
    }
    assert not has_required_keys(entry, required_keys)


def test_has_required_keys_empty_entry(required_keys):
    """Test the has all keys function with empty dict"""
    entry = {}

    assert not has_required_keys(entry, required_keys)


def test_is_dict_valid_dict(fake_product_data):
    """Test the is_dict function with a valid input"""
    assert is_dict(fake_product_data)


@pytest.mark.parametrize("entry", ['invalid', None, [], (11, 22), 12])
def test_is_dict_invalid_type(entry):
    """Test the is_dict function with a valid input"""
    assert is_dict(entry) is False


def test_has_correct_types_all_correct_types(fake_product_data, required_data_types):
    """Tests the function has_correct_types"""

    assert has_correct_types(fake_product_data, required_data_types)


def test_has_correct_types_incorrect_types(required_data_types):
    """Tests the function has_correct_types with invalid data"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': "12345",
        'product_name': 'adidas  trainers'
    }

    assert not has_correct_types(entry, required_data_types)


def test_has_correct_types_missing_key(required_data_types):
    """Tests the function has_correct_types with missing key"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': "12345",
    }

    assert not has_correct_types(entry, required_data_types)


def test_validate_input_valid(fake_product_list):
    """Tests the validate_input function"""
    validated_entries = validate_input(fake_product_list)

    assert len(validated_entries) == 2
    assert all(entry in fake_product_list for entry in validated_entries)


def test_validate_input_empty_list():
    """Tests the validate_input function with an empty list"""
    with pytest.raises(ValueError):
        result = validate_input([])
        assert "The list is empty after validation. Please provide a valid product list." in result

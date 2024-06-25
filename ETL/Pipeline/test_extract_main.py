"""This file tests whether the extract_combined file works as expected"""
from unittest.mock import patch
import pytest

from extract_main import (get_website_name, remove_stale_products,
                              extract_price_and_sales_data, process)


def test_get_website_name_with_valid_website_name(fake_product_data):
    """Tests the get_webiste_name works with valid data"""
    assert get_website_name(fake_product_data) == 'asos'


def test_get_website_name_without_website_name():
    """Tests the get_webiste_name returns None when missing website name"""
    product_data = {'product_id': 123, 'name': 'Product Name'}
    assert get_website_name(product_data) is None


def test_get_website_name_with_empty_dict():
    """Tests the get_webiste_name works returns None
    when an empty dic is passed"""
    product_data = {}
    assert get_website_name(product_data) is None


def test_get_website_name_with_non_dict_input():
    """Tests the get_website_name with a non dict entry"""
    with pytest.raises(TypeError):
        get_website_name(['not', 'a', 'dict'])


def test_remove_stale_products_valid_1():
    """Tests remove stale products with valid data"""
    fake_products = [
        {'previous_price': None,
         'current_price': 39.99}
    ]
    assert remove_stale_products(fake_products) == [
        {'previous_price': None,
         'current_price': 39.99}
    ]


def test_remove_stale_products_valid_2():
    """Tests remove stale products with valid data"""
    fake_products = [
        {'previous_price': 40.00,
         'current_price': 39.99}
    ]
    assert remove_stale_products(fake_products) == [
        {'previous_price': 40.00,
         'current_price': 39.99}
    ]


def test_remove_stale_products_valid_3():
    """Tests remove stale products with valid data"""
    fake_products = [
        {'previous_price': 30.00,
         'current_price': 39.99}
    ]
    assert remove_stale_products(fake_products) == [
    ]


@patch('extract_main.process')
@patch('extract_main.Pool')
def test_extract_price_and_sales_data_success(mock_Pool, mock_process, fake_product_list):
    """Tests the populate function"""
    extract_price_and_sales_data(fake_product_list)
    assert mock_Pool.return_value.__enter__.return_value.map.call_count == 1
    assert mock_Pool.return_value.__enter__.return_value.map.call_args[
        0][0] == mock_process
    assert mock_Pool.return_value.__enter__.return_value.map.call_args[
        0][1] == fake_product_list


@patch('extract_main.validate_input')
def test_process_invalid_validate_input(mock_validate_input, fake_product_data):
    """Tests the process function returns None on invalid input"""
    mock_validate_input.return_value = None
    result = process(fake_product_data)
    assert result is None


@patch('extract_main.get_website_name')
@patch('extract_main.validate_input')
def test_process_invalid_get_website_name(mock_validate_input,
                                          mock_get_website_name, fake_product_data):
    """Tests the process function returns None on no website name"""
    mock_validate_input.return_value = fake_product_data
    mock_get_website_name.return_value = None
    result = process(fake_product_data)
    assert result is None

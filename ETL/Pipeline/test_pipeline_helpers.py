"""This file tests whether the helpers file works as expected"""
from unittest.mock import patch
import pytest
import requests
from pipeline_helpers import (has_required_keys, has_correct_types,
                              validate_input, get_soup, get_product_page)


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


def test_validate_input_valid(fake_product_data):
    """Tests the validate_input function"""
    validated_entry = validate_input(fake_product_data)

    assert isinstance(validated_entry, dict)


def test_validate_input_invalid_input():
    """Tests the validate_input function with an invalid"""
    result = validate_input({"hi": "hello"})
    assert not result


@pytest.mark.parametrize("url", [None, 12.34, [1, 2, 3], (11, 22), {}, (), ["h", "b", "c"]])
def test_get_soup_invalid_url(fake_headers, url):
    """Tests get_soup with invalid url type"""
    with pytest.raises(TypeError):
        get_soup(url, fake_headers)


@pytest.mark.parametrize("headers", ['invalid', None, 12.34, [1, 2, 3], 1, (), ["h", "b", "c"]])
def test_get_soup_invalid_headers(headers, fake_url):
    """Tests get_soup with invalid headers type"""
    with pytest.raises(TypeError):
        get_soup(fake_url, headers=headers)


@patch('pipeline_helpers.requests.get')
def test_get_product_page_success(mock_get, fake_headers, fake_url):
    """Tests the get_product_page function passes with a valid URL"""
    mock_response = "<html><body><h1>Mock Product Page</h1></body></html>"
    mock_get.return_value.text = mock_response
    result = get_product_page(fake_url, fake_headers)
    assert result == mock_response
    assert mock_get.call_count == 1


@patch('pipeline_helpers.requests.get')
def test_get_product_page_timeout_exception(mock_get, fake_headers, fake_url):
    """Tests the get_product_page function raises a Timeout error"""
    mock_get.side_effect = requests.exceptions.Timeout
    product_page = get_product_page(fake_url, fake_headers)
    assert product_page is None


@patch('pipeline_helpers.requests.get')
def test_get_product_page_request_exception(mock_get, fake_headers, fake_url):
    """Tests the get_product_page function raises a RequestsException error"""
    mock_get.side_effect = requests.exceptions.RequestException
    product_page = get_product_page(fake_url, fake_headers)
    assert not product_page


@pytest.mark.parametrize("headers", ['invalid', None, 12.34, [1, 2, 3], 1, (), ["h", "b", "c"]])
def test_get_product_page_invalid_headers_type(fake_url, headers):
    """Tests get_product_page with invalid headers data type"""
    with pytest.raises(TypeError):
        get_product_page(fake_url, headers)


@pytest.mark.parametrize("url", [None, 12.34, [1, 2, 3], (11, 22), {}, (), ["h", "b", "c"]])
def test_get_product_page_invalid_url_type(fake_headers, url):
    """Tests get_product_page with invalid url type"""
    with pytest.raises(TypeError):
        get_product_page(url, fake_headers)


def test_get_product_page_empty_url(fake_headers):
    """Tests the get_product_page function returns none on an empty url"""
    product_page = get_product_page("", fake_headers)
    assert not product_page

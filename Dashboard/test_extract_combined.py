from unittest.mock import MagicMock, patch

import pytest

from extract_combined import (
    identify_store,
    get_website_id,
    extract_product_information
)

@patch('extract_combined.EXTRACT_FUNCTIONS', {'test_url': None})
def test_identify_store_valid_1():
    product_url = 'TEST_URL.com'
    assert identify_store(product_url) == 'test_url'

@patch('extract_combined.EXTRACT_FUNCTIONS', {'test_url': None})
def test_identify_store_valid_2():
    product_url = 'testing.com'
    assert identify_store(product_url) == None

@pytest.mark.parametrize('fake_urls', [2, 435, 234.0, [], {}])
def test_identify_store_invalid(fake_urls):
    with pytest.raises(TypeError):
        identify_store(fake_urls)

@patch('extract_combined.get_cursor')
def test_get_website_id(mock_get_cursor):
    mock_conn = MagicMock()
    mock_get_cursor.return_value.__enter__.return_value.fetchone.return_value = {'website_id': 1}
    assert get_website_id(mock_conn, 'test_url') == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1

@pytest.mark.parametrize('fake_product_urls', ['abcd', '234', [], 2342])
@patch('extract_combined.identify_store')
def test_extract_product_information_valid_1(mock_identify_store, fake_product_urls):
    mock_identify_store.return_value = None
    mock_conn = MagicMock()
    assert extract_product_information(mock_conn, fake_product_urls) == None
    assert mock_identify_store.call_count == 1
    assert mock_identify_store.call_args[0][0] == fake_product_urls

@pytest.mark.parametrize('fake_product', [['www.asos.com', 'asos'], ['www.patagonia.co.uk', 'patagonia'], ['www.steam.com', 'steam'], ['www.mango.co.uk', 'mango']])
@patch('extract_combined.get_website_id')
@patch('extract_combined.identify_store')
def test_extract_product_information_valid_2(mock_identify_store, mock_get_website_id, fake_product):
    mock_identify_store.return_value = fake_product[1]
    mock_get_website_id.return_value = None
    mock_conn = MagicMock()
    assert extract_product_information(mock_conn, fake_product[0]) == None
    assert mock_identify_store.call_count == 1
    assert mock_identify_store.call_args[0][0] == fake_product[0]
    assert mock_get_website_id.call_count == 1
    assert mock_get_website_id.call_args[0][0] == mock_conn
    assert mock_get_website_id.call_args[0][1] == fake_product[1]


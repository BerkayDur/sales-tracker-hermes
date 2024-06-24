from unittest.mock import MagicMock, patch

import pytest

from extract_combined import (
    identify_store,
    get_website_id,
    extract_product_information,
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
def test_identify_store_valid_2(fake_urls):
    with pytest.raises(TypeError):
        identify_store(fake_urls)

@patch('extract_combined.get_cursor')
def test_get_website_id(mock_get_cursor):
    mock_conn = MagicMock()
    mock_get_cursor.return_value.__enter__.return_value.fetchone.return_value = {'website_id': 1}
    assert get_website_id(mock_conn, 'test_url') == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1

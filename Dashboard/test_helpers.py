from unittest.mock import MagicMock, patch

import pytest
from botocore.client import BaseClient

from helpers import (get_product_page, is_ses)

@patch('requests.get')
def test_get_product_page_valid_1(mock_get):
    '''test get_product_page for a valid case'''
    fake_url = 'TEST_URL'
    fake_headers = {'FAKE_KEY_1': 'FAKE_VALUE_1',
                    'FAKE_KEY_2': 'FAKE_VALUE_2'}
    get_product_page(fake_url, fake_headers)
    assert mock_get.call_args[0][0] == fake_url
    assert mock_get.call_args[1]['headers'] == fake_headers
    assert mock_get.call_count == 1

@patch('requests.get')
def test_get_product_page_valid_empty_url(mock_get):
    '''test get_product_page for a valid case'''
    fake_url = ''
    fake_headers = {'FAKE_KEY_1': 'FAKE_VALUE_1',
                    'FAKE_KEY_2': 'FAKE_VALUE_2'}
    assert get_product_page(fake_url, fake_headers) == None
    assert mock_get.call_count == 0

@pytest.mark.parametrize('fake_url', [23, 435.0, [], {}])
@patch('requests.get')
def test_get_product_page_url_type_error(mock_get, fake_url):
    '''test get_product_page for a valid case'''
    fake_headers = {'FAKE_KEY_1': 'FAKE_VALUE_1',
                    'FAKE_KEY_2': 'FAKE_VALUE_2'}
    with pytest.raises(TypeError):
        assert get_product_page(fake_url, fake_headers)
    assert mock_get.call_count == 0

@pytest.mark.parametrize('fake_headers', ['', [], 223, 'hi'])
@patch('requests.get')
def test_get_product_page_headers_type_error(mock_get, fake_headers):
    '''test get_product_page for a valid case'''
    fake_url = 'TEST_URL'
    with pytest.raises(TypeError):
        assert get_product_page(fake_url, fake_headers)
    assert mock_get.call_count == 0

def test_is_ses_valid():
    '''test for valid.'''
    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    assert is_ses(mock_client)

@pytest.mark.parametrize('invalid_types', [
    [BaseClient, 's3'],
    [BaseClient, 'sns'],
    [BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
def test_is_ses_invalid(invalid_types):
    '''test for invalid types for ses client.'''
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    assert not is_ses(mock_client)
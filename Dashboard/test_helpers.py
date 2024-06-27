from unittest.mock import MagicMock, patch

import pytest
import psycopg2.extras
from psycopg2.extensions import connection
from botocore.client import BaseClient

from helpers import (
    get_cursor, get_product_page, is_ses,
    can_parse_as_float, get_supported_websites,
    get_user_id, get_product_id,
    is_subscription_in_table, insert_subscription_into_db,
    get_subscribed_products
    )


def test_get_cursor_valid():
    mock_conn = MagicMock(spec=connection)
    mock_conn.cursor.return_value = 'FAKE'
    assert get_cursor(mock_conn) == 'FAKE'
    assert mock_conn.cursor.call_count == 1
    assert mock_conn.cursor.call_args[1]['cursor_factory'] == psycopg2.extras.RealDictCursor

@pytest.mark.parametrize('bad_types', [int, float, str, list, dict])
def test_get_cursor_type_error(bad_types):
    mock_conn = MagicMock(spec=bad_types)
    mock_conn.cursor = MagicMock()
    with pytest.raises(TypeError):
        assert get_cursor(mock_conn) == 'FAKE'
    assert mock_conn.cursor.call_count == 0




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

@pytest.mark.parametrize('values', ['23.9', True, False, 23, 23.3,
                                    '23', '-25', '.23', '-.23'])
def test_can_parse_as_float_valid(values):
    assert can_parse_as_float(values)

@pytest.mark.parametrize('values', ['as2', '32a', {}, [], ''])
def test_can_parse_as_float_invalid(values):
    assert not can_parse_as_float(values)

@patch('helpers.get_cursor')
def test_get_supported_websites_valid_1(mock_get_cursor):
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.return_value = [{'website_name': 'asos'},
                                            {'website_name': 'mango'}]
    assert get_supported_websites(mock_conn) == ['asos', 'mango']
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.call_count == 1

@patch('helpers.get_cursor')
def test_get_supported_websites_valid_2(mock_get_cursor):
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.return_value = []
    assert get_supported_websites(mock_conn) == []
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.call_count == 1

@patch('helpers.get_cursor')
def test_get_user_id_valid_1(mock_get_cursor):
    fake_email = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = {'user_id': 5}
    assert get_user_id(mock_conn, fake_email) == 5
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_email,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@patch('helpers.get_cursor')
def test_get_user_id_valid_2(mock_get_cursor):
    fake_email = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = {}
    assert get_user_id(mock_conn, fake_email) == None
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_email,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@patch('helpers.get_cursor')
def test_get_user_id_valid_3(mock_get_cursor):
    fake_email = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = None
    assert get_user_id(mock_conn, fake_email) == None
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_email,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1


@patch('helpers.get_cursor')
def test_get_product_id_valid_1(mock_get_cursor):
    fake_url = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = {'product_id': 5}
    assert get_product_id(mock_conn, fake_url) == 5
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_url,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@patch('helpers.get_cursor')
def test_get_product_id_valid_2(mock_get_cursor):
    fake_url = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = {}
    assert get_product_id(mock_conn, fake_url) == None
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_url,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@patch('helpers.get_cursor')
def test_get_product_id_valid_3(mock_get_cursor):
    fake_url = 'FAKE.com'
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = None
    assert get_product_id(mock_conn, fake_url) == None
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_url,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1


@patch('helpers.get_cursor')
def test_is_subscription_in_table_valid_1(mock_get_cursor):
    fake_user_id = 5
    fake_product_id = 10
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = {}
    assert is_subscription_in_table(mock_conn, fake_user_id, fake_product_id)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_user_id, fake_product_id)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@patch('helpers.get_cursor')
def test_is_subscription_in_table_valid_2(mock_get_cursor):
    fake_user_id = 5
    fake_product_id = 10
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.return_value = None
    assert not is_subscription_in_table(mock_conn, fake_user_id, fake_product_id)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_user_id, fake_product_id)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_get_cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

@pytest.mark.parametrize('price_threshold', [None, 18, 1.00, 1.99])
@patch('helpers.get_cursor')
def test_insert_subscription_into_db_valid(mock_get_cursor, price_threshold):
    mock_conn = MagicMock(spec=connection)
    fake_user_id = 1
    fake_product_id = 2
    assert insert_subscription_into_db(mock_conn, fake_user_id, fake_product_id, price_threshold)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_user_id, fake_product_id, price_threshold)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_conn.commit.call_count == 1

@pytest.mark.parametrize('price_threshold', [0.00, 0, -0.01, -1])
@patch('helpers.get_cursor')
def test_insert_subscription_into_db_invalid_1(mock_get_cursor, price_threshold):
    mock_conn = MagicMock(spec=connection)
    fake_user_id = 1
    fake_product_id = 2
    assert not insert_subscription_into_db(mock_conn, fake_user_id, fake_product_id, price_threshold)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 0
    assert mock_conn.commit.call_count == 0

@pytest.mark.parametrize('exception_type', [TypeError, ValueError, psycopg2.errors.ConnectionFailure,
                                             psycopg2.errors.ConnectionDoesNotExist,
                                             psycopg2.errors.ConnectionFailure])
@patch('helpers.get_cursor')
def test_insert_subscription_into_db_invalid_2(mock_get_cursor, exception_type):
    mock_conn = MagicMock(spec=connection)
    fake_user_id = 1
    fake_product_id = 2
    fake_price_threshold = 11
    mock_get_cursor.return_value.__enter__\
     .return_value.execute.side_effect = exception_type
    assert not insert_subscription_into_db(mock_conn, fake_user_id, fake_product_id, fake_price_threshold)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_user_id, fake_product_id, fake_price_threshold)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_conn.commit.call_count == 0


@pytest.mark.parametrize('exception_type', [TypeError, ValueError, psycopg2.errors.ConnectionFailure,
                                             psycopg2.errors.ConnectionDoesNotExist,
                                             psycopg2.errors.ConnectionFailure])
@patch('helpers.get_cursor')
def test_insert_subscription_into_db_invalid_3(mock_get_cursor, exception_type):
    mock_conn = MagicMock(spec=connection)
    fake_user_id = 1
    fake_product_id = 2
    fake_price_threshold = 11
    mock_conn.commit.side_effect = exception_type
    assert not insert_subscription_into_db(mock_conn, fake_user_id, fake_product_id, fake_price_threshold)
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_user_id, fake_product_id, fake_price_threshold)
    assert mock_get_cursor.call_args[0][0] == mock_conn
    assert mock_conn.commit.call_count == 1

@patch('helpers.get_cursor')
def test_get_subscribed_products_valid_1(mock_get_cursor):
    fake_data= [
         {'product_id': 1, 'website_name': 'asos', 'url': 'www.asos.com', 'product_name': 'jeans', 'price_threshold': 10},
         {'product_id': 2, 'website_name': 'patagonia', 'url': 'www.patagonia.com', 'product_name': 'shorts', 'price_threshold': None}]
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.return_value = fake_data
    fake_email = 'FAKE.com'
    assert get_subscribed_products(mock_conn, fake_email) == fake_data
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_email,)
    assert mock_get_cursor.call_args[0][0] == mock_conn

@patch('helpers.get_cursor')
def test_get_subscribed_products_valid_2(mock_get_cursor):
    fake_data = []
    mock_conn = MagicMock(spec=connection)
    mock_get_cursor.return_value.__enter__\
     .return_value.fetchall.return_value = fake_data
    fake_email = 'FAKE.com'
    assert get_subscribed_products(mock_conn, fake_email) == fake_data
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == (fake_email,)
    assert mock_get_cursor.call_args[0][0] == mock_conn
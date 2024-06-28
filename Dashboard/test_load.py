from unittest.mock import MagicMock, patch

import pytest
from psycopg2.extensions import connection, cursor

from load import (
    verify_keys,
    insert_product_information
)


@pytest.mark.parametrize('inputs', [[['a', 'b', 'c'], set('abc')],
                                    [['a', 'b', 'c', 'd', 'e'], set('abc')],
                                    [[1, 2, 3], set([1, 2, 3])],
                                    [[1, 2, 3, 4, 5, 'a'], set([1, 2, 3])]])
def test_verify_keys_true(inputs):
    '''test verify_keys function for true cases.'''
    assert verify_keys(inputs[0], inputs[1])


@pytest.mark.parametrize('inputs', [[['a', 'b'], set('abc')],
                                    [['a', 'c', 'd', 'e'], set('abc')],
                                    [[], set([1, 2, 3])],
                                    [[1, 2, 5, 'a'], set([1, 2, 3])]])
def test_verify_keys_false(inputs):
    '''test verify_keys for false cases.'''
    assert not verify_keys(inputs[0], inputs[1])


@patch('load.get_cursor')
@patch('load.verify_keys')
def test_insert_product_information_valid(mock_verify_keys, mock_get_cursor):
    mock_verify_keys.return_value = True
    mock_conn = MagicMock(spec=connection)
    fake_data = {'url': 'FAKE1', 'product_name': 'FAKE2',
                 'product_code': 'FAKE3', 'website_id': 'FAKE4'}
    insert_product_information(mock_conn, fake_data)
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
        .return_value.execute.call_args[0][1] == (
            fake_data['website_id'], fake_data['url'],
            fake_data['product_code'], fake_data['product_name'])
    assert mock_conn.commit.call_count == 1


@pytest.mark.parametrize('conn_type', [str, float, int, dict, cursor])
def test_insert_product_information_type_error_1(conn_type):
    mock_conn = MagicMock(spec=conn_type)
    fake_data = {'a': 'b'}
    with pytest.raises(TypeError):
        insert_product_information(mock_conn, fake_data)


@patch('load.get_cursor')
@patch('load.verify_keys')
def test_insert_product_information_type_error_2(mock_verify_keys, mock_get_cursor):
    mock_verify_keys.return_value = False
    mock_conn = MagicMock(spec=connection)
    fake_data = {'url': 'FAKE1', 'product_name': 'FAKE2',
                 'exc': 'FAKE3', 'website_id': 'FAKE4'}
    with pytest.raises(TypeError):
        insert_product_information(mock_conn, fake_data)
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_conn.commit.call_count == 0


@pytest.mark.parametrize('fake_data', [[2, 3], (2, 4), '3453', 34])
@patch('load.get_cursor')
@patch('load.verify_keys')
def test_insert_product_information_type_error_3(mock_verify_keys, mock_get_cursor, fake_data):
    mock_conn = MagicMock(spec=connection)
    with pytest.raises(TypeError):
        insert_product_information(mock_conn, fake_data)
    assert mock_verify_keys.call_count == 0
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_conn.commit.call_count == 0

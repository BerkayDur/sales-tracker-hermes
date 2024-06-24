'''test file for combined_load.py'''

from unittest.mock import MagicMock, patch
from datetime import datetime

import pytest
from psycopg2.extensions import connection

from combined_load import (create_single_insert_format_string,
                           create_multiple_insert_format_string,
                           write_new_price_entries_to_db)


@pytest.mark.parametrize('inp_out', [[1, '(%s)'], [2, '(%s,%s)'], [3, '(%s,%s,%s)'],
                         [4, '(%s,%s,%s,%s)']])
def test_create_single_insert_format_string_valid(inp_out):
    '''test valid cases.'''
    assert create_single_insert_format_string(inp_out[0]) == inp_out[1]


@pytest.mark.parametrize('inp', ['1', '4', '-10', '324', 1.18, [], ('',)])
def test_create_single_insert_format_string_type_error(inp):
    '''test types errors.'''
    with pytest.raises(TypeError):
        create_single_insert_format_string(inp)


@pytest.mark.parametrize('inp', [0, -1, -2, -100, -50])
def test_create_single_insert_format_string_value_error(inp):
    '''check value error.'''
    with pytest.raises(ValueError):
        create_single_insert_format_string(inp)


@pytest.mark.parametrize('inp_out', [[2, '(%s)', '(%s), (%s);'],
                                     [3, '(%s)', '(%s), (%s), (%s);'],
                                     [2, '(%s,%s)', '(%s,%s), (%s,%s);'],
                                     [5, '(%s)', '(%s), (%s), (%s), (%s), (%s);'],
                                     [3, '(%s, %s, %s)',
                                      '(%s, %s, %s), (%s, %s, %s), (%s, %s, %s);'],
                                     [3, ':', ':, :, :;'],
                                     [2, 'Hello', 'Hello, Hello;']])
def test_create_multiple_insert_format_string_valid(inp_out):
    '''test valid cases.'''
    assert create_multiple_insert_format_string(
        inp_out[0], inp_out[1]) == inp_out[2]


@pytest.mark.parametrize('inp', ['1', '4', '-10', '324', 1.18, [], ('',)])
def test_create_multiple_insert_format_string_type_error_1(inp):
    '''test type error from invalid first input type.'''
    with pytest.raises(TypeError):
        create_multiple_insert_format_string(inp, ', ')


@pytest.mark.parametrize('inp', [1, True, 2.2, -32, [], {}])
def test_create_multiple_insert_format_string_type_error_2(inp):
    '''ttest type error from invalid second input type.'''
    with pytest.raises(TypeError):
        create_multiple_insert_format_string(1, inp)

@pytest.mark.parametrize('inp', [0, -1, -10, -5, -133])
def test_create_multiple_insert_format_string_value_error(inp):
    '''test value error for negative values.'''
    with pytest.raises(ValueError):
        create_multiple_insert_format_string(inp, ', ')

@patch('combined_load.create_multiple_insert_format_string')
@patch('combined_load.create_single_insert_format_string')
@patch('combined_load.get_cursor')
def test_write_new_price_entries_to_db_valid(mock_get_cursor,
                                             mock_create_single_insert_format_string,
                                             mock_create_multiple_insert_format_string,
                                             fake_products):
    '''test a valid case.'''
    mock_conn = MagicMock(spec=connection)
    write_new_price_entries_to_db(mock_conn, fake_products)
    assert mock_get_cursor.return_value.__enter__.call_count == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_args[0][1] == (
        1, datetime(2024, 6, 19, 17, 28), 83.99, 2, datetime(2024, 6, 19, 17, 28), 340.99, 3,
        datetime(2024, 6, 19, 17, 28), 18.99)
    assert mock_create_single_insert_format_string.call_count == 1
    assert mock_create_single_insert_format_string.call_args[0][0] == 3
    assert mock_create_multiple_insert_format_string.call_count == 1
    assert mock_create_multiple_insert_format_string.call_args[0][0] == 3

@pytest.mark.parametrize('fake_type', [int, bool, str, list, tuple, dict, float])
def test_write_new_price_entries_to_db_type_error_1(fake_type, fake_products):
    '''test for type error in connection obj.'''
    mock_conn = MagicMock(spec=fake_type)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)


@pytest.mark.parametrize('fake_products', [('',), '', 3, 23.23])
def test_write_new_price_entries_to_db_type_error_2(fake_products):
    '''check for type error in products'''
    mock_conn = MagicMock(spec=connection)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)

@pytest.mark.parametrize('fake_products', [[], ['', ''],[('',), ], [1,2,3]])
def test_write_new_price_entries_to_db_type_error_3(fake_products):
    '''test for type error in each product.'''
    mock_conn = MagicMock(spec=connection)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)

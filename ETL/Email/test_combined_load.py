import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

import psycopg2.extensions as psycopg2_types

from combined_load import create_single_insert_format_string, create_multiple_insert_format_string, write_new_price_entries_to_db


@pytest.mark.parametrize('inp_out', [[1, '(%s)'], [2, '(%s,%s)'], [3, '(%s,%s,%s)'],
                         [4, '(%s,%s,%s,%s)']])
def test_create_single_insert_format_string_valid(inp_out):
    assert create_single_insert_format_string(inp_out[0]) == inp_out[1]


@pytest.mark.parametrize('inp', ['1', '4', '-10', '324', 1.18, [], ('',)])
def test_create_single_insert_format_string_type_error(inp):
    with pytest.raises(TypeError):
        create_single_insert_format_string(inp)


@pytest.mark.parametrize('inp', [0, -1, -2, -100, -50])
def test_create_single_insert_format_string_value_error(inp):
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
    assert create_multiple_insert_format_string(
        inp_out[0], inp_out[1]) == inp_out[2]


@pytest.mark.parametrize('inp', ['1', '4', '-10', '324', 1.18, [], ('',)])
def test_create_multiple_insert_format_string_type_error_1(inp):
    with pytest.raises(TypeError):
        create_multiple_insert_format_string(inp, ', ')


@pytest.mark.parametrize('inp', [1, True, 2.2, -32, [], {}])
def test_create_multiple_insert_format_string_type_error_2(inp):
    with pytest.raises(TypeError):
        create_multiple_insert_format_string(1, inp)

@pytest.mark.parametrize('inp', [0, -1, -10, -5, -133])
def test_create_multiple_insert_format_string_value_error(inp):
    with pytest.raises(ValueError):
        create_multiple_insert_format_string(inp, ', ')

@patch('combined_load.create_multiple_insert_format_string')
@patch('combined_load.create_single_insert_format_string')
@patch('combined_load.get_cursor')
def test_write_new_price_entries_to_db_valid(mock_get_cursor, mock_create_single_insert_format_string, mock_create_multiple_insert_format_string, fake_products):
    mock_conn = MagicMock(spec=psycopg2_types.connection)
    write_new_price_entries_to_db(mock_conn, fake_products)
    assert mock_get_cursor.return_value.__enter__.call_count == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_args[0][1] == [1, datetime(2024, 6, 19, 17, 28), 83.99, 2, datetime(2024, 6, 19, 17, 28), 340.99, 3, datetime(2024, 6, 19, 17, 28), 18.99]
    assert mock_create_single_insert_format_string.call_count == 1
    assert mock_create_single_insert_format_string.call_args[0][0] == 3
    assert mock_create_multiple_insert_format_string.call_count == 1
    assert mock_create_multiple_insert_format_string.call_args[0][0] == 3

@pytest.mark.parametrize('fake_type', [int, bool, str, list, tuple, dict, float])
def test_write_new_price_entries_to_db_type_error_1(fake_type, fake_products):
    mock_conn = MagicMock(spec=fake_type)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)


@pytest.mark.parametrize('fake_products', [('',), '', 3, 23.23])
def test_write_new_price_entries_to_db_type_error_2(fake_products):
    mock_conn = MagicMock(spec=psycopg2_types.connection)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)

@pytest.mark.parametrize('fake_products', [[], ['', ''],[('',), ], [1,2,3]])
def test_write_new_price_entries_to_db_type_error_3(fake_products):
    mock_conn = MagicMock(spec=psycopg2_types.connection)
    with pytest.raises(TypeError):
        write_new_price_entries_to_db(mock_conn, fake_products)
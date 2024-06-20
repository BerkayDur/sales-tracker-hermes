from unittest.mock import MagicMock
import pytest

import botocore.client
import psycopg2.extensions as psycopg2_types

from helpers import get_cursor, is_ses

def test_get_cursor_valid():
    mock_connection = MagicMock(spec=psycopg2_types.connection)
    get_cursor(mock_connection)
    assert mock_connection.cursor.call_count == 1

@pytest.mark.parametrize('invalid_types', [int, float, str, list, tuple, dict, psycopg2_types.cursor])
def test_get_cursor_invalid_type(invalid_types):
    mock_connection = MagicMock(spec=invalid_types)
    mock_connection.cursor = MagicMock()
    with pytest.raises(TypeError):
        get_cursor(mock_connection)
    assert mock_connection.cursor.call_count == 0

def test_is_ses_valid():
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    assert is_ses(mock_client)

@pytest.mark.parametrize('invalid_types', [
    [botocore.client.BaseClient, 's3'],
    [botocore.client.BaseClient, 'sns'],
    [botocore.client.BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
def test_is_ses_invalid(invalid_types):
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    assert not is_ses(mock_client)
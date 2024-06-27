from unittest.mock import MagicMock, patch

import pytest
from psycopg2.extensions import connection

from login import (
    authenticate,
    add_email
)

def test_authenticate_valid_1():
    mock_conn = MagicMock(spec=connection)
    mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.return_value = ('FAKE_EMAIL',)
    assert authenticate(mock_conn, 'FAKE_EMAIL') == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

def test_authenticate_valid_2():
    mock_conn = MagicMock(spec=connection)
    mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.return_value = None
    assert authenticate(mock_conn, 'FAKE_EMAIL') == None
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1

def test_add_email_valid_1():
    mock_conn = MagicMock(spec=connection)
    mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.return_value = ('FAKE_EMAIL',)
    assert add_email(mock_conn, 'FAKE_EMAIL') == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1
    assert mock_conn.commit.call_count == 1

def test_add_email_valid_2():
    mock_conn = MagicMock(spec=connection)
    mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.return_value = None
    assert add_email(mock_conn, 'FAKE_EMAIL') == None
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_count == 1
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.execute.call_args[0][1] == ('FAKE_EMAIL',)
    assert mock_conn.cursor.return_value.__enter__\
     .return_value.fetchone.call_count == 1
    assert mock_conn.commit.call_count == 1
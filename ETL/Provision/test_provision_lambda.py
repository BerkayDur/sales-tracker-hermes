# pylint: skip-file
from provision_lambda import group_data, read_database
from unittest.mock import MagicMock
import pytest


@pytest.fixture
def fake_readings():
    return [{"product_id": 1, "url": "http://example.com/product1", "price": 19.99},
            {"product_id": 2, "url": "http://example.com/product2", "price": 24.99},
            {"product_id": 3, "url": "http://example.com/product3", "price": 12.34},
            {"product_id": 4, "url": "http://example.com/product4", "price": 228.99}]


def test_group_data_batch_of_2(fake_readings):
    readings = fake_readings
    assert group_data(readings, 2) == [[{"product_id": 1, "url": "http://example.com/product1", "price": 19.99},
                                       {"product_id": 2, "url": "http://example.com/product2",
                                           "price": 24.99}],
                                       [{"product_id": 3, "url": "http://example.com/product3",
                                           "price": 12.34},
                                       {"product_id": 4, "url": "http://example.com/product4", "price": 228.99}]]


def test_group_data_batch_of_30(fake_readings):
    readings = fake_readings
    assert group_data(readings, 30) == [[{"product_id": 1, "url": "http://example.com/product1", "price": 19.99},
                                         {"product_id": 2, "url": "http://example.com/product2",
                                          "price": 24.99},
                                         {"product_id": 3, "url": "http://example.com/product3",
                                          "price": 12.34},
                                         {"product_id": 4, "url": "http://example.com/product4", "price": 228.99}]]


def test_group_data_invalid_data():
    with pytest.raises(TypeError):
        group_data(
            {"product_id": 1, "url": "http://example.com/product1", "price": 19.99}, 2)


def test_group_data_invalid_product_data():
    with pytest.raises(TypeError):
        group_data(
            [{"product_id": 1, "url": "http://example.com/product1", "price": 19.99},
             ["product_id", 2, "url", "http://example.com/product2", "price", 24.99]], 2)


def test_read_database():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    read_database(mock_conn)

    mock_cursor.execute.assert_called_once()
    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT DISTINCT ON (product_id)" in call_args[0]
    assert "FROM products" in call_args[0]

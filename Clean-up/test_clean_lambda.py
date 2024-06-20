"""This file tests whether the clean_lambda file functions correctly"""

import json
from unittest.mock import patch, MagicMock

import pytest

from clean_lambda import delete_unsubscribed, handler


@pytest.fixture(name="unsubscribed_products")
def fixture_unsubscribed_products() -> list[dict]:
    """Example data for unsubscribed products"""
    return [{"product_id": 4, "url": "http://example.com/product4",
             "product_code": "P004", "product_name": "Product 4"},
            {"product_id": 5, "url": "http://example.com/product5",
             "product_code": "P005", "product_name": "Product 5"}]


def test_delete_unsubscribed(unsubscribed_products: list[dict]) -> None:
    """Tests the delete_unsubscribed function"""
    mock_conn = MagicMock()
    mock_cur = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cur

    mock_cur.fetchall.return_value = unsubscribed_products

    table = 'products'
    deleted_products = delete_unsubscribed(mock_conn, table)

    assert len(deleted_products) == len(unsubscribed_products)
    assert deleted_products == unsubscribed_products
    mock_cur.execute.assert_called_once_with(f"""
            DELETE FROM {table}
            WHERE product_id NOT IN (SELECT product_id FROM subscriptions)
            RETURNING *;""")
    mock_conn.commit.assert_called_once()


@patch('clean_lambda.get_connection')
@patch('clean_lambda.delete_unsubscribed')
def test_handler(mock_delete_unsubscribed, mock_get_connection,
                 unsubscribed_products: list[dict]) -> None:
    """Tests the handler function"""
    mock_delete_unsubscribed.return_value = unsubscribed_products
    mock_get_connection.return_value = MagicMock()

    result = handler({}, None)
    result_data = json.loads(result)

    assert "deleted_readings" in result_data
    assert "deleted_products" in result_data
    assert result_data["deleted_readings"] == unsubscribed_products
    assert result_data["deleted_products"] == unsubscribed_products

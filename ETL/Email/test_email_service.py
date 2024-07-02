"""Test file for email_service.py"""
from unittest.mock import MagicMock, patch

import pytest
from psycopg2.extensions import connection, cursor
import pandas as pd

from email_service import (
    verify_keys, get_customer_information, filter_merged_table,
    get_merged_customer_and_product_reading_table,
    group_by_email, format_email_from_data_frame,
    get_subject, get_html_unordered_list,
    create_email_body, get_formatted_email, get_email_list
)


@pytest.mark.parametrize("inputs", [[["a", "b", "c"], set("abc")],
                                    [["a", "b", "c", "d", "e"], set("abc")],
                                    [[1, 2, 3], set([1, 2, 3])],
                                    [[1, 2, 3, 4, 5, "a"], set([1, 2, 3])]])
def test_verify_keys_true(inputs):
    """test verify_keys function for true cases."""
    assert verify_keys(inputs[0], inputs[1])


@pytest.mark.parametrize("inputs", [[["a", "b"], set("abc")],
                                    [["a", "c", "d", "e"], set("abc")],
                                    [[], set([1, 2, 3])],
                                    [[1, 2, 5, "a"], set([1, 2, 3])]])
def test_verify_keys_false(inputs):
    """test verify_keys for false cases."""
    assert not verify_keys(inputs[0], inputs[1])


@patch("email_service.get_cursor")
@patch("email_service.create_single_insert_format_string")
def test_get_customer_information_valid(mock_create_single_insert_format_string,
                                        mock_get_cursor):
    """test get_customer_information for valid cases."""
    mock_conn = MagicMock(spec=connection)
    fake_product_ids = [1, 2, 3, 4]

    return_val = get_customer_information(mock_conn, fake_product_ids)
    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 1
    assert mock_get_cursor.return_value.__enter__\
        .return_value.execute.call_args[0][1] == fake_product_ids
    assert mock_create_single_insert_format_string.call_count == 1
    assert mock_create_single_insert_format_string.call_args[0][0] == 4
    assert isinstance(return_val, pd.DataFrame)


@pytest.mark.parametrize("inp", [str, float, int, dict, cursor])
@patch("email_service.get_cursor")
@patch("email_service.create_single_insert_format_string")
def test_get_customer_information_type_error_1(mock_create_single_insert_format_string,
                                               mock_get_cursor, inp):
    """test for type errors in connection object."""
    mock_conn = MagicMock(spec=inp)
    fake_product_ids = [1, 2, 3, 4]

    with pytest.raises(TypeError):
        get_customer_information(mock_conn, fake_product_ids)

    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_create_single_insert_format_string.call_count == 0


@pytest.mark.parametrize("fake_products", [{"dict": 1}, ("tuple",), 34, "22"])
@patch("email_service.get_cursor")
@patch("email_service.create_single_insert_format_string")
def test_get_customer_information_type_error_2(mock_create_single_insert_format_string,
                                               mock_get_cursor, fake_products):
    """test for type errors in products."""
    mock_conn = MagicMock(spec=connection)

    with pytest.raises(TypeError):
        get_customer_information(mock_conn, fake_products)

    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_create_single_insert_format_string.call_count == 0


@patch("email_service.get_cursor")
@patch("email_service.create_single_insert_format_string")
def test_get_customer_information_value_error(mock_create_single_insert_format_string,
                                              mock_get_cursor):
    """test for value errors in products (I.e., empty products list)."""
    mock_conn = MagicMock(spec=connection)

    with pytest.raises(ValueError):
        get_customer_information(mock_conn, [])

    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_create_single_insert_format_string.call_count == 0


@pytest.mark.parametrize("fake_products", [[1, 2, 3, 1.4], ["a", "b", 3], [1.3], [1, "2"]])
@patch("email_service.get_cursor")
@patch("email_service.create_single_insert_format_string")
def test_get_customer_information_type_error_3(mock_create_single_insert_format_string,
                                               mock_get_cursor, fake_products):
    """test for types errors in products (I.e., individual products aren"t the correct type.)"""
    mock_conn = MagicMock(spec=connection)

    with pytest.raises(TypeError):
        get_customer_information(mock_conn, fake_products)

    assert mock_get_cursor.return_value.__enter__.return_value.execute.call_count == 0
    assert mock_create_single_insert_format_string.call_count == 0


def test_filter_merged_table_valid(fake_merged_data):
    """testing filter_merged_table with valid DataFrame values."""
    assert filter_merged_table(fake_merged_data).sort_values("price_threshold").reset_index(drop=True).equals(pd.DataFrame([
        {"price_threshold": None, "current_price": 18.96,
            "price": 19.98, "is_on_sale": True},
        {"price_threshold": 19.99, "current_price": 18.91,
            "price": None, "is_on_sale": False},
        {"price_threshold": 19.98, "current_price": 18.90,
            "price": None, "is_on_sale": True},
        {"price_threshold": 19.96, "current_price": 18.88,
            "price": 20.99, "is_on_sale": True},
        {"price_threshold": 19.95, "current_price": 18.87,
            "price": 20.98, "is_on_sale": False},
    ]).sort_values("price_threshold").reset_index(drop=True))


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_filter_merged_table_invalid(fake_data):
    """testing filter_merged_table with invalid type (I.e., not a DataFrame)."""
    with pytest.raises(TypeError):
        filter_merged_table(fake_data)


@patch("email_service.filter_merged_table")
def test_get_merged_customer_and_product_reading_table_valid(mock_filter_merged_table):
    """test for a valid case (mostly to check call arguments, etc.)"""
    fake_customer_information = pd.DataFrame(
        [{"product_id": 1, "price_threshold": 10.0}])
    fake_product_reading = pd.DataFrame(
        [{"product_id": 1, "current_price": 10.0, "is_on_sale": True}])
    get_merged_customer_and_product_reading_table(fake_customer_information,
                                                  fake_product_reading)
    assert mock_filter_merged_table.call_count == 1
    assert mock_filter_merged_table.call_args[0][0].equals(pd.DataFrame(
        [{"product_id": 1, "price_threshold": 10.0, "current_price": 10.0, "is_on_sale": True}]))


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_get_merged_customer_and_product_reading_table_type_error_1(fake_data):
    """test for types error in customer_data."""
    fake_product_reading = pd.DataFrame(
        [{"product_id": 1, "current_price": 10.0, "is_on_sale": True}])
    with pytest.raises(TypeError):
        get_merged_customer_and_product_reading_table(
            fake_data, fake_product_reading)


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_get_merged_customer_and_product_reading_table_type_error_2(fake_data):
    """test for type errors in product ireading."""
    fake_customer_information = pd.DataFrame(
        [{"product_id": 1, "price_threshold": 10.0}])
    with pytest.raises(TypeError):
        get_merged_customer_and_product_reading_table(
            fake_customer_information, fake_data)


def test_group_by_email_valid():
    """test for valid case."""
    fake_data = pd.DataFrame([{"email": "bob", "id": 0},
                              {"email": "jimbo", "id": 1},
                              {"email": "bob", "id": 2}])
    fake_email = "bob"
    assert group_by_email(fake_data, fake_email).equals(pd.DataFrame(
        [{"email": "bob", "id": 0}, {"email": "bob", "id": 2}], index=[0, 2]))


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_group_by_email_type_error_1(fake_data):
    """test for type error in fake customer email data."""
    fake_email = "bob"
    with pytest.raises(TypeError):
        group_by_email(fake_data, fake_email)


@pytest.mark.parametrize("fake_email", [5, 345.0, [], pd.DataFrame()])
def test_group_by_email_type_error_2(fake_email):
    """test for type errors in an email."""
    fake_data = pd.DataFrame([{"email": "bob", "id": 0},
                              {"email": "jimbo", "id": 1},
                              {"email": "bob", "id": 2}])
    with pytest.raises(TypeError):
        group_by_email(fake_data, fake_email)


def test_format_email_from_data_frame_valid_1():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": None, "is_on_sale": False,
                               "product_name": "TEST1", "price": 2.00,
                               "current_price": 1.00, "url": "TEST2", "website_name": "asos"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(asos) <a href=\"TEST2\">TEST1</a> was £2.0, now £1.0."
    assert not out["email_type"]


def test_format_email_from_data_frame_valid_2():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 2.00, "is_on_sale": False,
                               "product_name": "TEST1", "price": 2.00,
                               "current_price": 1.00, "url": "TEST2", "website_name": "test"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(test) <a href=\"TEST2\">TEST1</a> was £2.0, now £1.0."
    assert out["email_type"] == "threshold"


def test_format_email_from_data_frame_valid_3():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 0.50, "is_on_sale": True,
                               "product_name": "TEST1", "price": 2.00,
                               "current_price": 1.00, "url": "TEST2", "website_name": "martin"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(martin) <a href=\"TEST2\">TEST1</a> was £2.0, now £1.0."
    assert out["email_type"] == "sale"


def test_format_email_from_data_frame_valid_4():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 1.00, "is_on_sale": True,
                               "product_name": "TEST1", "price": 2.00,
                               "current_price": 1.00, "url": "TEST2", "website_name": "asos"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(asos) <a href=\"TEST2\">TEST1</a> was £2.0, now £1.0 (ON SALE)."
    assert out["email_type"] == "threshold"


def test_format_email_from_data_frame_valid_5():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": None, "is_on_sale": False,
                               "product_name": "TEST1", "price": float("nan"),
                               "current_price": 1.00, "url": "TEST2", "website_name": "diff"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(diff) <a href=\"TEST2\">TEST1</a> now £1.0."
    assert not out["email_type"]


def test_format_email_from_data_frame_valid_6():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 2.00, "is_on_sale": False,
                               "product_name": "TEST1", "price": float("nan"),
                               "current_price": 1.00, "url": "TEST2", "website_name": "rand"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(rand) <a href=\"TEST2\">TEST1</a> now £1.0."
    assert out["email_type"] == "threshold"


def test_format_email_from_data_frame_valid_7():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 0.50, "is_on_sale": True,
                               "product_name": "TEST1", "price": float("nan"),
                               "current_price": 1.00, "url": "TEST2", "website_name": "asos"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(asos) <a href=\"TEST2\">TEST1</a> now £1.0."
    assert out["email_type"] == "sale"


def test_format_email_from_data_frame_valid_8():
    """test for valid"""
    fake_row_data = pd.Series({"price_threshold": 1.00, "is_on_sale": True,
                               "product_name": "TEST1", "price": float("nan"),
                               "current_price": 1.00, "url": "TEST2", "website_name": "asos"})
    out = format_email_from_data_frame(fake_row_data)
    assert out["message"] == "(asos) <a href=\"TEST2\">TEST1</a> now £1.0 (ON SALE)."
    assert out["email_type"] == "threshold"


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.DataFrame([{"product_id": 1, "price_threshold": 10.0}])])
def test_format_email_from_data_frame_type_error(fake_data):
    """test for type errors in email types."""
    with pytest.raises(TypeError):
        format_email_from_data_frame(fake_data)


def test_get_subject_valid_1():
    """test for valid"""
    email_types = pd.Series(["threshold"])
    assert get_subject(email_types) == "Tracked product(s) below threshold!"


def test_get_subject_valid_2():
    """test for valid"""
    email_types = pd.Series(["sale"])
    assert get_subject(email_types) == "Tracked product(s) on sale!"


def test_get_subject_valid_3():
    """test for valid"""
    email_types = pd.Series(["sale", "threshold"])
    assert get_subject(email_types) == "Tracked products price decrease!"


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.DataFrame([{"product_id": 1, "price_threshold": 10.0}])])
def test_get_subject_type_error(fake_data):
    """test for type error in email types"""
    with pytest.raises(TypeError):
        assert get_subject(fake_data)


def test_get_html_unordered_list_valid_1():
    """test for valid"""
    content = ["a", "b", "c"]
    assert get_html_unordered_list(
        content) == "<ul><li>a</li><li>b</li><li>c</li></ul>"


def test_get_html_unordered_list_valid_2():
    """test for valid"""
    content = []
    assert get_html_unordered_list(content) == ""


@pytest.mark.parametrize("fake_data", [tuple(), {}, (1, 2, 3,), 23])
def test_get_html_unordered_list_type_error_1(fake_data):
    """test for type error in email content."""
    with pytest.raises(TypeError):
        get_html_unordered_list(fake_data)


@pytest.mark.parametrize("fake_data", [["a", "b", 1], ["a", 23], [[]]])
def test_get_html_unordered_list_type_error_2(fake_data):
    """test for type error in nested values in email content."""
    with pytest.raises(TypeError):
        get_html_unordered_list(fake_data)


@patch("email_service.get_html_unordered_list")
def test_create_email_body_valid_1(mock_get_html_unordered_list):
    """test for valid"""
    fake_data = pd.DataFrame([{"email_type": "threshold", "message": "a"},
                              {"email_type": "threshold", "message": "b"}])
    mock_get_html_unordered_list.side_effect = ["", "a"]
    out = create_email_body(fake_data)
    assert mock_get_html_unordered_list.call_args[0][0] == ["a", "b"]
    assert mock_get_html_unordered_list.call_count == 2
    assert out == "<p>The following tracked products have crossed your threshold!</p>a"


@patch("email_service.get_html_unordered_list")
def test_create_email_body_valid_2(mock_get_html_unordered_list):
    """test for valid"""
    fake_data = pd.DataFrame([{"email_type": "sale", "message": "a"},
                              {"email_type": "sale", "message": "b"}])
    mock_get_html_unordered_list.side_effect = ["a", ""]
    out = create_email_body(fake_data)
    assert mock_get_html_unordered_list.call_args[0][0] == []
    assert mock_get_html_unordered_list.call_count == 2
    assert out == "<p>The following tracked products are on SALE!</p>a"


@patch("email_service.get_html_unordered_list")
def test_create_email_body_valid_3(mock_get_html_unordered_list):
    """test for valid"""
    fake_data = pd.DataFrame([{"email_type": "sale", "message": "a"},
                              {"email_type": "threshold", "message": "b"}])
    mock_get_html_unordered_list.side_effect = ["a", "b"]
    out = create_email_body(fake_data)
    assert mock_get_html_unordered_list.call_args[0][0] == ["b"]
    assert mock_get_html_unordered_list.call_count == 2
    assert out == ("<p>The following tracked products have crossed your threshold!</p>b" +
                   "<p>The following tracked products are on SALE!</p>a")


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_create_email_body_type_error(fake_data):
    """test for type error for content to create email body."""
    with pytest.raises(TypeError):
        create_email_body(fake_data)


@patch("pandas.DataFrame.apply")
@patch("email_service.create_email_body")
@patch("email_service.get_subject")
@patch("email_service.format_email_from_data_frame")
def test_get_formatted_email_valid(mock_format_email_from_data_frame,
                                   mock_get_subject, mock_create_email_body,
                                   mock_dataframe_apply):
    """test for valid"""
    fake_data = pd.DataFrame([{"email": "TEST1", "email_type": "TEST2"},
                              {"email": "TEST1", "email_type": "TEST3"}])
    mock_format_email_from_data_frame.return_value = "a"
    mock_get_subject.return_value = "b"
    mock_create_email_body.return_value = "c"
    assert list(get_formatted_email(fake_data).keys()) == [
        "recipient", "subject", "body"]
    assert mock_dataframe_apply.call_count == 1
    assert mock_get_subject.call_count == 1
    assert mock_create_email_body.call_count == 1


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_get_formatted_email_type_error(fake_data):
    """test for type error in email data."""
    with pytest.raises(TypeError):
        get_formatted_email(fake_data)


@patch("email_service.is_ses")
def test_get_email_list_valid(mock_is_ses):
    """test for valid"""
    fake_data = pd.Series(["TEST1", "TEST2", "TEST3"])
    fake_ses_client = MagicMock()
    mock_is_ses.return_value = True
    fake_ses_client.list_verified_email_addresses.return_value = {
        "VerifiedEmailAddresses": ["TEST1", "TEST2"]}
    assert get_email_list(fake_data, fake_ses_client) == set(
        ["TEST1", "TEST2"])


@pytest.mark.parametrize("fake_data", [[{"product_id": 1, "price_threshold": 10.0}],
                                       {"product_id": 1, "price_threshold": 10.0},
                                       pd.Series([{"product_id": 1, "price_threshold": 10.0}])])
def test_get_email_list_type_error_1(fake_data):
    """test for type error in email list data."""
    fake_ses_client = MagicMock()
    with pytest.raises(TypeError):
        get_email_list(fake_data, fake_ses_client)


@patch("email_service.is_ses")
def test_get_email_list_type_error_2(mock_is_ses):
    """test for type error in ses client."""
    fake_data = pd.Series(["TEST1", "TEST2", "TEST3"])
    fake_ses_client = MagicMock()
    mock_is_ses.return_value = False
    with pytest.raises(TypeError):
        get_email_list(fake_data, fake_ses_client)

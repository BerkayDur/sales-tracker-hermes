from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from extract_from_asos import (
    is_correct_page,
    scrape_product_information,
    get_product_code_asos,
    get_product_name_asos
)


@pytest.mark.parametrize("valid_outputs", [1, 2, 3, " ", {"rand": 2}])
def test_is_correct_page_valid(valid_outputs):
    mock_soup = MagicMock(spec=BeautifulSoup)
    mock_soup.find.return_value = valid_outputs
    assert is_correct_page(mock_soup) == True
    assert mock_soup.find.call_count == 1
    assert mock_soup.find.call_args[0][0] == "div"
    assert mock_soup.find.call_args[1]["attrs"] == {"class": "single-product"}


def test_is_correct_page_invalid():
    mock_soup = MagicMock(spec=BeautifulSoup)
    mock_soup.find.return_value = None
    assert is_correct_page(mock_soup) == False
    assert mock_soup.find.call_count == 1
    assert mock_soup.find.call_args[0][0] == "div"
    assert mock_soup.find.call_args[1]["attrs"] == {"class": "single-product"}


@pytest.mark.parametrize("bad_type", [str, list, dict, int])
def test_is_correct_page_type_error(bad_type):
    mock_soup = MagicMock(spec=bad_type)
    mock_soup.find = MagicMock()
    with pytest.raises(TypeError):
        is_correct_page(mock_soup)
    assert mock_soup.find.call_count == 0


@patch("json.loads")
def test_scape_product_information_valid(mock_loads):
    mock_loads.return_value = "FAKE"

    mock_soup = MagicMock(spec=BeautifulSoup)
    mock_soup.find = MagicMock()
    mock_soup.find.return_value = MagicMock()
    mock_soup.find.return_value.string = "STRING"

    assert scrape_product_information(mock_soup) == "FAKE"
    assert mock_soup.find.call_count == 1
    assert mock_soup.find.call_args[0][0] == "script"
    assert mock_soup.find.call_args[1]["type"] == "application/ld+json"
    assert mock_loads.call_args[0][0] == "STRING"
    assert mock_loads.call_count == 1


@patch("json.loads")
def test_scape_product_information_invalid(mock_loads):
    mock_loads.return_value = "FAKE"

    mock_soup = MagicMock(spec=BeautifulSoup)
    mock_soup.find = MagicMock()
    mock_soup.find.return_value = None

    assert scrape_product_information(mock_soup) == None
    assert mock_soup.find.call_count == 1
    assert mock_soup.find.call_args[0][0] == "script"
    assert mock_soup.find.call_args[1]["type"] == "application/ld+json"
    assert mock_loads.call_count == 0


@pytest.mark.parametrize("bad_type", [str, list, dict, int])
@patch("json.loads")
def test_scape_product_information_type_error(mock_loads, bad_type):
    mock_soup = MagicMock(spec=bad_type)
    mock_soup.find = MagicMock()
    with pytest.raises(TypeError):
        scrape_product_information(mock_soup)
    assert mock_soup.find.call_count == 0
    assert mock_loads.call_count == 0


def test_get_product_code_asos_valid_1():
    fake_product_data = {"productID": 1234}
    assert get_product_code_asos(fake_product_data) == "1234"


def test_get_product_code_asos_valid_2():
    fake_product_data = {"@graph": [{"productID": 5678}]}
    assert get_product_code_asos(fake_product_data) == 5678


def test_get_product_code_asos_valid_3():
    fake_product_data = {"another_id": 3}
    assert get_product_code_asos(fake_product_data) == None


def test_get_product_code_asos_valid_4():
    fake_product_data = {}
    assert get_product_code_asos(fake_product_data) == None


@pytest.mark.parametrize("fake_product_data", [[], tuple(), set(), 2234, 34.04])
def test_get_product_code_asos_type_error(fake_product_data):
    with pytest.raises(TypeError):
        get_product_code_asos(fake_product_data)


def test_get_product_name_asos_valid_1():
    fake_product_data = {"name": "fake"}
    assert get_product_name_asos(fake_product_data) == "fake"


def test_get_product_name_asos_valid_2():
    fake_product_data = {"@graph": [{"name": "fake2"}]}
    assert get_product_name_asos(fake_product_data) == "fake2"


def test_get_product_name_asos_valid_3():
    fake_product_data = {"another_id": "fake3"}
    assert get_product_name_asos(fake_product_data) == None


def test_get_product_name_asos_valid_4():
    fake_product_data = {}
    assert get_product_name_asos(fake_product_data) == None


@pytest.mark.parametrize("fake_product_data", [[], tuple(), set(), 2234, 34.04])
def test_get_product_name_asos_type_error(fake_product_data):
    with pytest.raises(TypeError):
        get_product_name_asos(fake_product_data)

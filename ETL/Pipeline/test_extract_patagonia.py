"""This file tests whether the extract_patagonia file works as expected"""
from unittest.mock import patch, MagicMock

from bs4 import BeautifulSoup
import pytest

from extract_patagonia import (get_product_info, get_current_price,
                               get_sale_status, process_product, is_correct_page)


def test_get_product_info_valid():
    """Tests the get_product_info works with a valid input."""
    html = '<span class="js-buy-config-price">Product Info</span>'
    soup = BeautifulSoup(html, 'html.parser')
    result = get_product_info(soup)
    assert result is not None
    assert result.text == "Product Info"


def test_get_product_info_invalid_type():
    """Tests the get_product_info raises a TypeError with invalid
    data type."""
    with pytest.raises(TypeError):
        get_product_info("not a BeautifulSoup object")


def test_get_product_info_no_product_info():
    """Tests the get_product_info returns None if no data found."""
    html = '<div>No product info here</div>'
    soup = BeautifulSoup(html, 'html.parser')
    result = get_product_info(soup)
    assert result is None


def test_get_product_info_with_buy_config_price():
    """Tests the get_product_info works."""
    html = '<span class="buy-config-price">Buy Config Info</span>'
    soup = BeautifulSoup(html, 'html.parser')
    result = get_product_info(soup)
    assert result is not None
    assert result.text == "Buy Config Info"


def test_get_current_price_valid():
    """Tests the get current price with valid input"""
    html = '''
    <span class="js-buy-config-price">
        <span class="sales">
            <span class="value" content="100"></span>
        </span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='js-buy-config-price')
    result = get_current_price(soup)
    assert result == 100


def test_get_current_price_invalid_type():
    """Tests the get current price with invalid type"""
    with pytest.raises(TypeError):
        get_current_price("not a Tag object")


# def test_get_current_price_no_sales_span():
#     html = '''
#     <span class="js-buy-config-price">
#         <span class="value" content="100"></span>
#     </span>
#     '''
#     soup = BeautifulSoup(html, 'html.parser').find(
#         'span', class_='js-buy-config-price')
#     result = get_current_price(soup)
#     print(result)
#     assert result is None


# def test_get_current_price_no_value_span():
#     html = '''
#     <span class="js-buy-config-price">
#         <span class="sales"></span>
#     </span>
#     '''
#     soup = BeautifulSoup(html, 'html.parser').find(
#         'span', class_='js-buy-config-price')
#     result = get_current_price(soup)
#     assert result is None


def test_get_current_price_invalid_content():
    """Tests the get current price with invalid contents"""
    html = '''
    <span class="js-buy-config-price">
        <span class="sales">
            <span class="value" content="invalid"></span>
        </span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='js-buy-config-price')
    with pytest.raises(ValueError):
        get_current_price(soup)


def test_get_sale_status_valid_on_sale():
    """Tests the get sale status with a discount percentage."""
    html = '''
    <span class="product-info">
        <span class="discount-percentage">10%</span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='product-info')
    result = get_sale_status(soup)
    assert result is True


def test_get_sale_status_valid_not_on_sale():
    """Tests the get sale status with no discount percentage."""
    html = '''
    <span class="product-info">
        <span class="discount-percentage"></span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='product-info')
    result = get_sale_status(soup)
    assert result is False


def test_get_sale_status_no_discount_span():
    """Tests the get sale status function """
    html = '''
    <span class="product-info">
        <span class="price">100</span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='product-info')
    result = get_sale_status(soup)
    assert result is False


def test_get_sale_status_invalid_type():
    """Tests the get sale status function """
    with pytest.raises(TypeError):
        get_sale_status("not a Tag object")


def test_get_sale_status_no_text_in_discount():
    """Tests the get sale status function with no text in discount"""
    html = '''
    <span class="product-info">
        <span class="discount-percentage"> </span>
    </span>
    '''
    soup = BeautifulSoup(html, 'html.parser').find(
        'span', class_='product-info')
    result = get_sale_status(soup)
    assert result is False


def test_is_correct_page_valid():
    """Tests the is correct page function with valid data"""
    html = '''
    <div class="product-detail">
        <p>Product details here.</p>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = is_correct_page(soup)
    assert result is True


def test_is_correct_page_invalid_type():
    """Tests the is correct page function with invalid data"""
    with pytest.raises(TypeError):
        is_correct_page("not a BeautifulSoup object")


def test_is_correct_page_no_product_detail():
    """Tests the is correct page function with no product detail"""
    html = '''
    <div class="other-detail">
        <p>Some other details here.</p>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = is_correct_page(soup)
    assert result is False


def test_is_correct_page_empty_html():
    """Tests the is correct page function with empty html"""
    html = ''
    soup = BeautifulSoup(html, 'html.parser')
    result = is_correct_page(soup)
    assert result is False


def test_is_correct_page_nested_product_detail():
    """Tests the is correct page function with product data"""
    html = '''
    <div>
        <div class="product-detail">
            <p>Product details here.</p>
        </div>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    result = is_correct_page(soup)
    assert result is True


@patch('extract_patagonia.get_soup')
@patch('extract_patagonia.is_correct_page')
def test_process_product_invalid_page(mock_is_correct_page, mock_get_soup):
    """Tests the process product works with invalid page"""
    mock_get_soup.return_value = MagicMock()
    mock_is_correct_page.return_value = False

    product = {
        "url": "https://www.example.com/product-page",
        "product_code": "12345"
    }

    with pytest.raises(ValueError):
        process_product(product)


@patch('extract_patagonia.get_soup')
@patch('extract_patagonia.is_correct_page')
@patch('extract_patagonia.get_product_info')
def test_process_product_no_product_info(mock_get_product_info, mock_is_correct_page,
                                         mock_get_soup):
    """Tests the process product with no product infor"""
    mock_get_soup.return_value = MagicMock()
    mock_is_correct_page.return_value = True
    mock_get_product_info.return_value = None

    product = {
        "url": "https://www.example.com/product-page",
        "product_code": "12345"
    }
    result = process_product(product)
    assert result is None

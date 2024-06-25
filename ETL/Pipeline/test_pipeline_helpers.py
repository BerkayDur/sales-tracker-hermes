"""This file tests whether the helpers file works as expected"""

from pipeline_helpers import has_required_keys, has_correct_types, validate_input


def test_has_required_keys_all_keys_present(required_keys, fake_product_data):
    """Test the has all keys function with valid data"""
    assert has_required_keys(fake_product_data, required_keys)


def test_has_required_keys_missing_keys(required_keys):
    """Test the has all keys function with missing keys"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': 12345
    }
    assert not has_required_keys(entry, required_keys)


def test_has_required_keys_empty_entry(required_keys):
    """Test the has all keys function with empty dict"""
    entry = {}

    assert not has_required_keys(entry, required_keys)


def test_has_correct_types_all_correct_types(fake_product_data, required_data_types):
    """Tests the function has_correct_types"""

    assert has_correct_types(fake_product_data, required_data_types)


def test_has_correct_types_incorrect_types(required_data_types):
    """Tests the function has_correct_types with invalid data"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': "12345",
        'product_name': 'adidas  trainers'
    }

    assert not has_correct_types(entry, required_data_types)


def test_has_correct_types_missing_key(required_data_types):
    """Tests the function has_correct_types with missing key"""
    entry = {
        'product_id': 1,
        'url': "https://www.asos.com/adidas",
        'product_code': "12345",
    }

    assert not has_correct_types(entry, required_data_types)


def test_validate_input_valid(fake_product_data):
    """Tests the validate_input function"""
    validated_entry = validate_input(fake_product_data)

    assert isinstance(validated_entry, dict)


def test_validate_input_invalid_input():
    """Tests the validate_input function with an invalid"""
    result = validate_input({"hi": "hello"})
    assert not result

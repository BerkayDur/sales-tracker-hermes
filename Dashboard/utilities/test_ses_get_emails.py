'''contains test files for ses_get_emails.py'''

from unittest.mock import MagicMock, patch

import pytest
import botocore.client

from ses_get_emails import (is_ses, get_all_ses_emails,
                            get_verified_ses_emails,
                            get_unverified_ses_emails)

def test_is_ses_valid():
    '''test for a valid ses client.'''
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
    '''test for invalid types for ses client.'''
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    assert not is_ses(mock_client)

@patch('ses_get_emails.is_ses')
def test_get_all_ses_emails_valid(mock_is_ses):
    '''test for valid types for ses client.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_identities = MagicMock()
    mock_client.list_identities.return_value = {
        'Identities' : ['TEST1', 'TEST2']
    }
    assert get_all_ses_emails(mock_client) == ['TEST1', 'TEST2']
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_identities.call_count == 1
    assert mock_client.list_identities.call_args[1]['IdentityType'] == 'EmailAddress'

@patch('ses_get_emails.is_ses')
def test_get_all_ses_emails_valid_empty(mock_is_ses):
    '''test for valid types for ses client with empty return.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_identities = MagicMock()
    mock_client.list_identities.return_value = {
        'Identities' : []
    }
    assert get_all_ses_emails(mock_client) == []
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_identities.call_count == 1
    assert mock_client.list_identities.call_args[1]['IdentityType'] == 'EmailAddress'


@pytest.mark.parametrize('invalid_types', [
    [botocore.client.BaseClient, 's3'],
    [botocore.client.BaseClient, 'sns'],
    [botocore.client.BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
@patch('ses_get_emails.is_ses')
def test_get_all_ses_emails_bad_client(mock_is_ses, invalid_types):
    '''test for invalid types for ses client.'''
    mock_is_ses.return_value = False
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    mock_client.list_identities = MagicMock()
    assert get_all_ses_emails(mock_client) == []
    assert mock_is_ses.call_count == 1
    assert mock_client.list_identities.call_count == 0

@patch('ses_get_emails.is_ses')
def test_get_verified_ses_emails_valid(mock_is_ses):
    '''test for valid types for ses client.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_verified_email_addresses = MagicMock()
    mock_client.list_verified_email_addresses.return_value = {
        'VerifiedEmailAddresses' : ['TEST1', 'TEST2']
    }
    assert get_verified_ses_emails(mock_client) == ['TEST1', 'TEST2']
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_verified_email_addresses.call_count == 1

@patch('ses_get_emails.is_ses')
def test_get_verified_ses_emails_valid_empty(mock_is_ses):
    '''test for valid types for ses client with empty return.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_verified_email_addresses = MagicMock()
    mock_client.list_verified_email_addresses.return_value = {
        'VerifiedEmailAddresses' : []
    }
    assert get_verified_ses_emails(mock_client) == []
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_verified_email_addresses.call_count == 1

@pytest.mark.parametrize('invalid_types', [
    [botocore.client.BaseClient, 's3'],
    [botocore.client.BaseClient, 'sns'],
    [botocore.client.BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
@patch('ses_get_emails.is_ses')
def test_get_verified_ses_emails_bad_client(mock_is_ses, invalid_types):
    '''test for invalid types for ses client.'''
    mock_is_ses.return_value = False
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    mock_client.list_verified_email_addresses = MagicMock()
    assert get_verified_ses_emails(mock_client) == []
    assert mock_is_ses.call_count == 1
    assert mock_client.list_verified_email_addresses.call_count == 0


@pytest.mark.parametrize('all_verified_out', [
    [['TEST1', 'TEST2'], ['TEST1', 'TEST2'], []],
    [[], [], []],
    [['TEST1', 'TEST2', 'TEST3'], ['TEST1', 'TEST2'], ['TEST3']]
])
@patch('ses_get_emails.get_verified_ses_emails')
@patch('ses_get_emails.get_all_ses_emails')
@patch('ses_get_emails.is_ses')
def test_get_unverified_ses_emails_valid(
    mock_is_ses, mock_get_all_ses_emails, mock_get_verified_ses_emails,
    all_verified_out):
    '''test for valid types for ses client.'''
    mock_is_ses.return_value = True
    mock_get_all_ses_emails.return_value = all_verified_out[0]
    mock_get_verified_ses_emails.return_value = all_verified_out[1]

    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'

    assert get_unverified_ses_emails(mock_client) == all_verified_out[2]
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_get_all_ses_emails.call_args[0][0] == mock_client
    assert mock_get_all_ses_emails.call_count == 1
    assert mock_get_verified_ses_emails.call_args[0][0] == mock_client
    assert mock_get_verified_ses_emails.call_count == 1


@pytest.mark.parametrize('invalid_types', [
    [botocore.client.BaseClient, 's3'],
    [botocore.client.BaseClient, 'sns'],
    [botocore.client.BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
@patch('ses_get_emails.get_verified_ses_emails')
@patch('ses_get_emails.get_all_ses_emails')
@patch('ses_get_emails.is_ses')
def test_get_unverified_ses_emails_bad_client(
    mock_is_ses, mock_get_all_ses_emails, mock_get_verified_ses_emails,
    invalid_types):
    '''test for invalid types for ses client.'''
    mock_is_ses.return_value = False
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    mock_client.list_verified_email_addresses = MagicMock()
    assert get_unverified_ses_emails(mock_client) == []
    assert mock_is_ses.call_count == 1
    assert mock_get_all_ses_emails.call_count == 0
    assert mock_get_verified_ses_emails.call_count == 0

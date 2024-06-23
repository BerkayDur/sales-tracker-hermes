'''contains test files for ses_get_emails.py'''

from unittest.mock import MagicMock, patch

import pytest
import botocore.client

from ses_get_emails import (is_ses, get_ses_emails)

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
def test_get_ses_emails_valid_all(mock_is_ses):
    '''test get_ses_emails for all emails.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_identities = MagicMock()
    mock_client.list_identities.return_value = {
        'Identities' : ['TEST1', 'TEST2']
    }
    assert get_ses_emails(mock_client, 'all') == ['TEST1', 'TEST2']
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_identities.call_count == 1
    assert mock_client.list_identities.call_args[1]['IdentityType'] == 'EmailAddress'

@patch('ses_get_emails.is_ses')
def test_get_ses_emails_valid_verified(mock_is_ses):
    '''test get_ses_emails for only verified emails.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_verified_email_addresses = MagicMock()
    mock_client.list_verified_email_addresses.return_value = {
        'VerifiedEmailAddresses' : ['TEST1', 'TEST2']
    }
    assert get_ses_emails(mock_client, 'verified') == ['TEST1', 'TEST2']
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_verified_email_addresses.call_count == 1



@patch('ses_get_emails.is_ses')
@pytest.mark.parametrize('all_verified_out', [
    [['TEST1', 'TEST2'], ['TEST1', 'TEST2'], []],
    [[], [], []],
    [['TEST1', 'TEST2', 'TEST3'], ['TEST1', 'TEST2'], ['TEST3']],
    [['TEST1'], ['TEST1'], []],
])
def test_get_ses_emails_valid_unverified(mock_is_ses, all_verified_out):
    '''test get_ses_emails for only unverified emails.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_identities = MagicMock()
    mock_client.list_identities.return_value = {
        'Identities' : all_verified_out[0]
    }
    mock_client.list_verified_email_addresses = MagicMock()
    mock_client.list_verified_email_addresses.return_value = {
        'VerifiedEmailAddresses' : all_verified_out[1]
    }
    assert get_ses_emails(mock_client, 'unverified') == all_verified_out[2]
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_identities.call_count == 1
    assert mock_client.list_identities.call_args[1]['IdentityType'] == 'EmailAddress'
    assert mock_client.list_verified_email_addresses.call_count == 1


@pytest.mark.parametrize('bad_method', ['bob', 2, 234, '', 'this',
                                        'that', 'over', 'under'])
@patch('ses_get_emails.is_ses')
def test_get_ses_emails_invalid(mock_is_ses, bad_method):
    '''test get_ses_emails for an invalid case where method is not
    one of the enumerated values.'''
    mock_is_ses.return_value = True
    mock_client = MagicMock(spec=botocore.client.BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.list_identities = MagicMock()
    mock_client.list_verified_email_addresses = MagicMock()

    assert get_ses_emails(mock_client, bad_method) == []
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.list_identities.call_count == 0
    assert mock_client.list_verified_email_addresses.call_count == 0

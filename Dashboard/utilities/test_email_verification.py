'''contains test files for email_verification.py'''
from unittest.mock import MagicMock, patch

import pytest
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from email_verification import (is_ses, send_verification_email)

def test_is_ses_valid():
    '''test for valid.'''
    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    assert is_ses(mock_client)

@pytest.mark.parametrize('invalid_types', [
    [BaseClient, 's3'],
    [BaseClient, 'sns'],
    [BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
def test_is_ses_invalid(invalid_types):
    '''test for invalid types for ses client.'''
    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    assert not is_ses(mock_client)

@patch('email_verification.is_ses')
def test_email_verification_valid(mock_is_ses):
    '''test email verification with a valid input.'''
    mock_is_ses.return_value = True

    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()
    mock_client.verify_email_identity.return_value = {
        'ResponseMetadata' : {
            'RequestId' : 'FAKE REQUEST ID'
        }
    }

    assert send_verification_email(mock_client, 'test@mail.com') == {'success': True, 'request_id': 'FAKE REQUEST ID'}
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 1
    assert mock_client.verify_email_identity.call_args[1]['EmailAddress'] == 'test@mail.com'


@pytest.mark.parametrize('bad_value', [5, 23, 232.0, [], tuple(), set(), {}])
def test_email_verification_invalid_email_type(bad_value):
    '''test email verification with a valid input.'''
    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()

    assert send_verification_email(mock_client, bad_value) == {
        'success': False,
        'reason': 'bad email type, email must be of type str.'}
    assert mock_client.verify_email_identity.call_count == 0


@pytest.mark.parametrize('invalid_types', [
    [BaseClient, 's3'],
    [BaseClient, 'sns'],
    [BaseClient, 'ec2'],
    [float, 's3'],
    [dict, 'ses'],
])
@patch('email_verification.is_ses')
def test_email_verification_invalid_client(mock_is_ses, invalid_types):
    '''test email verification with invalid client.'''
    mock_is_ses.return_value = False

    mock_client = MagicMock(spec=invalid_types[0])
    mock_client._service_model = MagicMock()
    mock_client._service_model.service_name = invalid_types[1]
    mock_client.verify_email_identity = MagicMock()

    assert send_verification_email(mock_client, 'test@mail.com') == {
        'success': False, 'reason': 'client is not a boto3 ses client.'}
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 0

@patch('email_verification.is_ses')
def test_email_verification_bad_email_error(mock_is_ses):
    '''test email verification with a bad email input.'''
    mock_is_ses.return_value = True

    e = {'Error': {'Code': 'InvalidParameterValue'}}

    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()
    mock_client.verify_email_identity.side_effect = ClientError(e, 'VerifyEmailIdentity')
    out = send_verification_email(mock_client, 'fakemail.com')
    assert out['success'] == False
    assert out['reason'] == 'invalid email address format.'
    assert out['error'] == e
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 1
    assert mock_client.verify_email_identity.call_args[1]['EmailAddress'] == 'fakemail.com'

@patch('email_verification.is_ses')
def test_email_verification_bad_credentials_error(mock_is_ses):
    '''test email verification with a bad aws credentials.'''
    mock_is_ses.return_value = True

    e = {'Error': {'Code': 'InvalidClientTokenId'}}

    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()
    mock_client.verify_email_identity.side_effect = ClientError(e, 'InvalidParameterValue')
    out = send_verification_email(mock_client, 'fake@mail.com')
    assert out['success'] == False
    assert out['reason'] == 'bad aws credentials!'
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 1
    assert mock_client.verify_email_identity.call_args[1]['EmailAddress'] == 'fake@mail.com'

@patch('email_verification.is_ses')
def test_email_verification_unknown_error_1(mock_is_ses):
    '''test email verification with unknown error.'''
    mock_is_ses.return_value = True

    e = {'Error': {'Code': 'FAKE_ERROR'}}

    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()
    mock_client.verify_email_identity.side_effect = ClientError(e, 'FAKE_ERROR')
    out = send_verification_email(mock_client, 'fake@mail.com')
    assert out['success'] == False
    assert out['reason'] == 'failure for unknown reason, see field \'error\''
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 1
    assert mock_client.verify_email_identity.call_args[1]['EmailAddress'] == 'fake@mail.com'

@patch('email_verification.is_ses')
def test_email_verification_unknown_error_2(mock_is_ses):
    '''test email verification with unknown error.'''
    mock_is_ses.return_value = True

    e = {}

    mock_client = MagicMock(spec=BaseClient)
    mock_client._service_model.service_name = 'ses'
    mock_client.verify_email_identity = MagicMock()
    mock_client.verify_email_identity.side_effect = ClientError(e, 'FAKE_ERROR')
    out = send_verification_email(mock_client, 'fake@mail.com')
    assert out['success'] == False
    assert out['reason'] == 'unknown reason, but no Error attribute on response, see field \'error\'!'
    assert mock_is_ses.call_count == 1
    assert mock_is_ses.call_args[0][0] == mock_client
    assert mock_client.verify_email_identity.call_count == 1
    assert mock_client.verify_email_identity.call_args[1]['EmailAddress'] == 'fake@mail.com'
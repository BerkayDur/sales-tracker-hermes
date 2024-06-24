'''utility functions to add unverified email to ses and send verification emails.'''

from os import environ as CONFIG
import logging

from dotenv import load_dotenv

from boto3 import client as boto_client
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import mypy_boto3_ses.client as ses_client


def get_ses_client(config: dict) -> ses_client:
    '''Returns an ses client from a configuration.'''
    return boto_client(
        'ses',
        aws_access_key_id=config["ACCESS_KEY"],
        aws_secret_access_key=config['SECRET_ACCESS_KEY'],
        region_name='eu-west-2'
    )


def is_ses(boto_ses_client: ses_client) -> bool:
    '''Returns true if ses client else false.'''
    return (isinstance(boto_ses_client, BaseClient)
            and boto_ses_client._service_model.service_name == 'ses')  # pylint: disable=protected-access


def send_verification_email(boto_ses_client: ses_client, email: str) -> dict[bool, str]:
    '''adds email as unverified email to ses and send a verification email.
    Returns a dictionary containing fields:
            success    : True if sending email verification was a success, else False
            reason     : If success is False, return a reason for failure
            error      : If success is False, return an error object (only if types are correct)
            request_id : If success is True, return a request id for that email verification.
    '''
    if not isinstance(email, str):
        logging.error(
            'send_verification_email passed `email` argument not of type str.')
        return {'success': False, 'reason': 'bad email type, email must be of type str.'}
    if not is_ses(boto_ses_client):
        logging.error(
            'send_verification_email client is not a boto3 ses client.')
        return {'success': False, 'reason': 'client is not a boto3 ses client.'}
    logging.info('Sending email verification...')
    try:
        response = boto_ses_client.verify_email_identity(EmailAddress=email)
    except ClientError as e:
        if not e.response.get('Error'):
            logging.error('sending email verification failed due to an unknown reason\
 (no Error attribute on response object), see field \'error\'!')
            reason = 'unknown reason, but no Error attribute on response, see field \'error\'!'
        elif e.response.get('Error').get('Code') == 'InvalidClientTokenId':
            logging.error(
                'sending email verification failed due to bad aws credentials!')
            reason = 'bad aws credentials!'
        elif e.response.get('Error').get('Code') == 'InvalidParameterValue':
            logging.error(
                'sending email verification failed due to bad email address format!')
            reason = 'invalid email address format.'
        else:
            logging.error(
                'sending email verification failed due to an unknown reason!')
            reason = 'failure for unknown reason, see field \'error\''
        return {'success': False, 'reason': reason, 'error': e.response}
    logging.info('Sending email verification success!')
    return {'success': True, 'request_id': response.get('ResponseMetadata').get('RequestId')}


if __name__ == '__main__':
    load_dotenv()
    logging.basicConfig(level='INFO')

    client = get_ses_client(CONFIG)

    print(send_verification_email(client, 'fake@mail.com'))

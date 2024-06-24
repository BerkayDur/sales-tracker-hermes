'''utility functions to get all/verified/unverified emails from ses.'''

from os import environ as CONFIG
import logging

from dotenv import load_dotenv

from boto3 import client as boto_client
from botocore.client import BaseClient
from mypy_boto3_ses.client import SESClient as ses_client

def get_ses_client(config: dict) -> ses_client:
    '''Returns an ses client from a configuration.'''
    return boto_client(
        'ses',
        aws_access_key_id = config["ACCESS_KEY"],
        aws_secret_access_key = config['SECRET_ACCESS_KEY'],
        region_name = config['AWS_REGION_NAME']
    )

def is_ses(boto_ses_client: ses_client) -> bool:
    '''Returns true if ses client else false.'''
    return (isinstance(boto_ses_client, BaseClient)
            and boto_ses_client._service_model.service_name == 'ses') #pylint: disable=protected-access

def get_ses_emails(boto_ses_client: ses_client, method: str) -> list[str]:
    '''Given a boto3 ses client a method, return a list of emails.

    Method is an enumerated with 3 possible values:
        'all'
        'verified'
        'unverified'
    '''
    if not is_ses(boto_ses_client):
        logging.error('client passed to get_ses_emails is not a boto3 ses client.')
        return []
    if method == 'all':
        logging.info('Getting all ses emails.')
        return boto_ses_client.list_identities(IdentityType="EmailAddress")['Identities']
    if method == 'verified':
        logging.info('Getting all verified ses emails.')
        return boto_ses_client.list_verified_email_addresses()['VerifiedEmailAddresses']
    if method == 'unverified':
        logging.info('Getting all unverified ses emails.')
        all_emails = boto_ses_client.list_identities(IdentityType="EmailAddress")['Identities']
        verified_emails = boto_ses_client.list_verified_email_addresses()['VerifiedEmailAddresses']
        return list(set(all_emails) - set(verified_emails))
    logging.error('method passed to get_ses_method must be one of the following enumerated values\
`all`, `verified`, `unverified`, you passed %s of type %s', method, type(method))
    return []

if __name__ == '__main__':
    logging.basicConfig(level='INFO')

    load_dotenv()
    client = get_ses_client(CONFIG)
    test_all_emails = get_ses_emails(client, 'all')
    test_verified_emails = get_ses_emails(client, 'verified')
    test_unverified_emails = get_ses_emails(client, 'unverified')
    print(len(test_all_emails))
    print(len(test_verified_emails))
    print(len(test_unverified_emails))

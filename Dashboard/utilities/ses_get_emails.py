'''utility functions to get all/verified/unverified emails from ses.'''

from os import environ as CONFIG
import logging

from dotenv import load_dotenv

from boto3 import client as boto_client
from botocore.client import BaseClient
import mypy_boto3_ses.client as ses_client

def get_ses_client(config: dict) -> ses_client:
    '''Returns an ses client from a configuration.'''
    return boto_client(
        'ses',
        aws_access_key_id = config["ACCESS_KEY"],
        aws_secret_access_key = config['SECRET_ACCESS_KEY'],
        region_name='eu-west-2'
    )

def is_ses(boto_ses_client: ses_client) -> bool:
    '''Returns true if ses client else false.'''
    return (isinstance(boto_ses_client, BaseClient)
            and boto_ses_client._service_model.service_name == 'ses') #pylint: disable=protected-access

def get_all_ses_emails(boto_ses_client: ses_client) -> list[str]:
    '''returns all ses emails'''
    if not is_ses(boto_ses_client):
        logging.error('client passed to get_all_ses_emails is not a boto3 ses client.')
        return []
    return boto_ses_client.list_identities(IdentityType="EmailAddress")['Identities']


def get_verified_ses_emails(boto_ses_client: ses_client) -> list[str]:
    '''returns verified ses emails'''
    if not is_ses(boto_ses_client):
        logging.error('client passed to get_verified_ses_emails is not a boto3 ses client.')
        return []
    return boto_ses_client.list_verified_email_addresses()['VerifiedEmailAddresses']

def get_unverified_ses_emails(boto_ses_client: ses_client) -> list[str]:
    '''returns unverified ses emails'''
    if not is_ses(boto_ses_client):
        logging.error('client passed to get_unverified_ses_emails is not a boto3 ses client.')
        return []
    all_emails = get_all_ses_emails(boto_ses_client)
    verified_emails = get_verified_ses_emails(boto_ses_client)
    return list(set(all_emails) - set(verified_emails))

if __name__ == '__main__':
    logging.basicConfig(level='INFO')

    load_dotenv()
    client = get_ses_client(CONFIG)
    test_all_emails = get_all_ses_emails(client)
    test_verified_emails = get_verified_ses_emails(client)
    test_unverified_emails = get_unverified_ses_emails(client)
    print(len(test_all_emails))
    print(len(test_verified_emails))
    print(len(test_unverified_emails))

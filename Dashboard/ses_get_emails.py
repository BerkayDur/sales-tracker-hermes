'''utility functions to get all/verified/unverified emails from ses.'''

import logging

from mypy_boto3_ses.client import SESClient as ses_client

from helpers import is_ses

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

def is_ses_verified(ses_client: ses_client, email: str) -> bool:
    '''Checks if an email is verified'''
    if not isinstance(email, str):
        return False
    return email in get_ses_emails(ses_client, 'verified')

if __name__ == '__main__':
    logging.basicConfig(level='INFO')

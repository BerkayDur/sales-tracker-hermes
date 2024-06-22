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

def is_ses(client: ses_client) -> bool:
    '''Returns true if ses client else false.'''
    return (isinstance(client, BaseClient)
            and client._service_model.service_name == 'ses') #pylint: disable=protected-access


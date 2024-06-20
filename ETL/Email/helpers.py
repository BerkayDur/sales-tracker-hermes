'''Contains some helpers that is used throughout this directory'''

import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.extensions as psycopg2_types

import boto3
import botocore
import botocore.client
import botocore.exceptions
import mypy_boto3_ses.client as SES_CLIENT


def get_connection(config: dict) -> psycopg2_types.connection:
    '''Get psycopg2 connection object to database'''
    return psycopg2.connect(
        host=config['DB_HOST'],
        port=config['DB_PORT'],
        dbname=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD']
    )

def get_cursor(connection: psycopg2_types.connection) -> psycopg2_types.cursor:
    '''Get a psycopg2 cursor using the configuration of a RealDictCursor'''
    if not isinstance(connection, psycopg2_types.connection):
        raise TypeError('connection must be of a psycopg2 ')
    return connection.cursor(cursor_factory=RealDictCursor)

def get_ses_client(config: dict) -> SES_CLIENT:
    '''Returns an ses client from a configuration.'''
    access_key = config["ACCESS_KEY"]
    secret_access_key = config['SECRET_ACCESS_KEY']
    return boto3.client(
        'ses',
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_access_key
    )

def is_ses(client: SES_CLIENT) -> bool:
    '''Returns true if ses client else false.'''
    return (isinstance(client, botocore.client.BaseClient)
            and client._service_model.service_name == 'ses') #pylint: disable=protected-access

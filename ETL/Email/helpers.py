'''Contains some helpers that is used throughout this directory'''

import logging

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection, cursor

from boto3 import client as boto_client
from botocore.client import BaseClient
import mypy_boto3_ses.client as ses_client


def get_connection(config: dict) -> connection:
    '''Get psycopg2 connection object to database'''
    return psycopg2.connect(
        host=config['DB_HOST'],
        port=config['DB_PORT'],
        dbname=config['DB_NAME'],
        user=config['DB_USER'],
        password=config['DB_PASSWORD']
    )

def get_cursor(conn: connection) -> cursor:
    '''Get a psycopg2 cursor using the configuration of a RealDictCursor'''
    if not isinstance(conn, connection):
        logging.error('Connection must be of a psycopg2 connection object.')
        raise TypeError('Connection must be of a psycopg2 connection object.')
    return conn.cursor(cursor_factory=RealDictCursor)

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

def filter_on_current_price_less_than_previous_price(price_reading):
    '''Provides a filter on the current price being less than the previous price.'''
    return ((not price_reading['previous_price']) or
            price_reading['current_price'] < price_reading['previous_price'])
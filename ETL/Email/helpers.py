'''Contains some helpers that is used throughout this directory'''

import psycopg2
from psycopg2.extras import RealDictCursor
import psycopg2.extensions as psycopg2_types

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
    return connection.cursor(cursor_factory=RealDictCursor)

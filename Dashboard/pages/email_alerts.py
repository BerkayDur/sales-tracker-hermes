"""Email alerts page for StreamLit"""
from os import environ as CONFIG
from time import sleep

import streamlit as st
from mypy_boto3_ses.client import SESClient as ses_client

from navigation import make_sidebar # pylint: disable=import-error
from helpers import (get_ses_client) # pylint: disable=import-error
from ses_get_emails import is_ses_verified # pylint: disable=import-error
from email_verification import send_verification_email, unverify_email # pylint: disable=import-error

def email_alerts_page(boto_ses_client: ses_client):
    '''Contains the StreamLit email alerts page'''

    st.title('Email Alerts')

    if is_ses_verified(boto_ses_client, st.session_state['email']):
        if st.button('Unsubscribe from Email Alerts!'):
            unverify_email(boto_ses_client, st.session_state['email'])
            st.warning('You are now unsubscribed from Email Alerts!')
            sleep(1)
            st.rerun()
    else:
        send_verification_email(boto_ses_client, st.session_state['email'])
        if st.button('Subscribe to Email Alerts!'):
            st.warning('Check your inbox!')

if __name__ == '__main__':
    client = get_ses_client(CONFIG)
    make_sidebar()
    email_alerts_page(client)

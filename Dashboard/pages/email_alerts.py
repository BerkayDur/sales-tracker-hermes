"""Email alerts page for StreamLit"""
from os import environ as CONFIG
from time import sleep
import logging

import streamlit as st
from mypy_boto3_ses.client import SESClient as ses_client

from navigation import make_sidebar # pylint: disable=import-error
from helpers import (get_ses_client) # pylint: disable=import-error
from ses_get_emails import is_ses_verified # pylint: disable=import-error
from email_verification import send_verification_email, unverify_email # pylint: disable=import-error
from custom_styling import apply_custom_styling # pylint: disable=import-error

def email_alerts_page(boto_ses_client: ses_client):
    '''Contains the StreamLit email alerts page'''

    st.title('Subscribe to email alerts')
    st.markdown('Subscribe to stay alerted on price drops for your favourite products.')
    st.text('')
    if is_ses_verified(boto_ses_client, st.session_state['email']):
        if st.button('Unsubscribe from Email Alerts!'):
            logging.info('Trying to unsubscribe from email alerts.')

            unverify_email(boto_ses_client, st.session_state['email'])
            logging.info('Successfully unsubscribed from email alerts.')
            st.warning('You are now unsubscribed from Email Alerts!')
            sleep(1)
            st.rerun()
    else:
        col1, col2 = st.columns([1, 8])
        with col1:
            email_sign_up = st.button('Sign me up!')
        if email_sign_up:
            send_verification_email(boto_ses_client, st.session_state['email'])

            with col2:
                if st.button('Unsubscribe!'):
                    unverify_email(boto_ses_client, st.session_state['email'])
            logging.info('Sent user email verification.')
            st.warning('Action required: confirm your email subscription')

if __name__ == '__main__':
    client = get_ses_client(CONFIG)
    apply_custom_styling()
    make_sidebar()
    email_alerts_page(client)


"""Email alerts page for StreamLit"""
from os import _Environ, environ as CONFIG
from time import sleep

import streamlit as st

from navigation import make_sidebar
from utils.ses_get_emails import get_ses_client, get_ses_emails
from utils.email_verification import send_verification_email, unverify_email

def is_verified(_ses_client, email: str) -> bool:
    '''Checks if an email is verified'''
    return email in get_ses_emails(_ses_client, 'verified')

def email_alerts_page(config: _Environ):
    '''Contains the StreamLit email alerts page'''

    st.title('Email Alerts')
    ses_client = get_ses_client(config)

    if is_verified(ses_client, st.session_state['email']):
        if st.button('Unsubscribe from Email Alerts!'):
            unverify_email(ses_client, st.session_state['email'])
            st.warning('You are now unsubscribed from Email Alerts!')
            sleep(1)
            st.rerun()
    else:
        send_verification_email(ses_client, st.session_state['email'])
        if st.button('Subscribe to Email Alerts!'):
            st.warning('Check your inbox!')
    # else:
    #     st.write('Verify your email to receive email alerts!')
    #     col1, col2 = st.columns([3,10])
    #     with col1:
    #         if st.session_state.get('email_verification_sent'):
    #             verify_email_button = st.button('Send another verification email!')

    #         else:
    #             verify_email_button = st.button('Send verification email!')
    #     if verify_email_button:
    #         st.session_state['email_verification_sent'] = True
    #         send_verification_email(ses_client, st.session_state['email'])
    #     if st.session_state.get('email_verification_sent'):
    #         st.warning('Email verification sent, please check your inbox!')
    #         with col2:
    #             if st.button('Confirm Verification.'):
    #                 if is_verified(ses_client, st.session_state['email']):
    #                     st.success('You are now subscribed to receive email verifications!')
    #                 else:
    #                     st.warning('Please check you inbox to confirm email verification')


if __name__ == '__main__':
    make_sidebar()
    email_alerts_page(CONFIG)
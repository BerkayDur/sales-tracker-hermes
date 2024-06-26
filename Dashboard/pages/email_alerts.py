
"""Email alerts page for StreamLit"""
from os import _Environ, environ as CONFIG

import streamlit as st

from navigation import make_sidebar
from utils.ses_get_emails import get_ses_client, get_ses_emails
from utils.email_verification import send_verification_email

def is_verified(_ses_client, email: str) -> bool:
    '''Checks if an email is verified'''
    return email in get_ses_emails(_ses_client, 'verified')

def email_alerts_page(config: _Environ):
    '''Contains the StreamLit email alerts page'''
    ses_client = get_ses_client(config)
    if is_verified(ses_client, st.session_state['email']):
        st.write('Your email is verified, you will receive email alerts!')
    else:
        st.write('Your email is not verified! Subscribe to receive email alerts!')
        if st.button('Verify email!'):
            send_verification_email(ses_client, st.session_state['email'])
            if st.button('Confirm Verification.'):
                st.rerun()


if __name__ == '__main__':
    make_sidebar()
    email_alerts_page(CONFIG)
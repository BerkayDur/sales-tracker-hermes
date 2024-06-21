"""Login page for streamlit"""

import streamlit as st

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


def authenticate(email) -> bool:
    """Function to authenticate email"""
    return "@" in email and "." in email


def login_page() -> None:
    """Login page"""
    st.title("Login Page")

    email = st.text_input("Please enter your email to access the website:")

    if st.button("Login"):
        st.write(email)
        if authenticate(email):
            st.success(f"Welcome! You are logged in with email: {email}")
            st.session_state.logged_in = True
            st.session_state.email = email
            st.experimental_rerun()
        else:
            st.error("Invalid email address. Please try again.")


def main() -> None:
    if st.session_state.logged_in:
        st.switch_page("pages/1_price.py")
    else:
        login_page()


if __name__ == "__main__":
    main()

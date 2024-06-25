"""Controls the sidebar for streamlit"""

from time import sleep

import streamlit as st
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages


def get_current_page_name() -> str | None:
    """Gets the name of the page"""
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash].get("page_name")


def make_sidebar() -> None:
    """Creates sidebar"""
    page_name = get_current_page_name()
    if page_name:
        st.query_params["page"] = page_name

    with st.sidebar:
        st.title("💎 Sales tracker")
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            st.page_link("pages/price.py",
                         label="Price Tracker", icon="💵")

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif page_name != "login":
            st.switch_page("login.py")


def logout() -> None:
    """Logs out of account"""
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("login.py")

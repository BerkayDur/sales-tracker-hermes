"""Price tracker page for streamlit"""

import streamlit as st


def price_tracker_page() -> None:
    """Product Price Tracker Page"""
    st.title("Product Price Tracker")

    with st.expander("List of Compatible websites", expanded=True):
        st.write("ASOS")

    product_url = st.text_input("Enter the product URL:")

    if st.button("Track Price"):
        if product_url:
            subscribe(product_url)
        else:
            st.error("Please enter a valid product URL.")


def subscribe(product_url):
    """Tracks product"""
    exist = check_url_exists(product_url)
    if exist:
        return st.success(
            "Product url is already being tracked. You have been subscribed.")

    price = get_price(product_url)
    if price:
        return st.success(f"The current price of the product is: {price}")
    return st.error("Unable to fetch the price. Please check the URL.")


def check_url_exists(product_url) -> bool:
    return False


def get_price(product_url) -> str:
    return "£20"


def main() -> None:
    """Checking login information"""
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        price_tracker_page()
    else:
        st.error("Please log in to access this page.")


if __name__ == "__main__":
    main()

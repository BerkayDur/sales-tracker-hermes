"""Price tracker page for streamlit"""

import streamlit as st


def price_tracker_page() -> None:
    """Product Price Tracker Page"""
    st.title("Product Price Tracker")

    product_url = st.text_input("Enter the product URL:")

    if st.button("Track Price"):
        if product_url:
            price = "£20"
            if price:
                st.success(f"The current price of the product is: {price}")
            else:
                st.error(
                    "Unable to fetch the price. Please check the URL or try again later.")
        else:
            st.error("Please enter a valid product URL.")


def main() -> None:
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        price_tracker_page()
    else:
        st.error("Please log in to access this page.")


if __name__ == "__main__":
    main()

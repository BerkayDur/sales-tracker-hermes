import streamlit as st

from helpers import extract_website_name, MatchingError, WEBSITES




def get_product_url() -> str:
    product_url = st.text_input(label="Enter product url:")
    if product_url:
        try:
            st.write(extract_website_name(product_url))
        except MatchingError:
            st.write('No matches.')
    return product_url


if __name__ == '__main__':
    if 'products' not in st.session_state:
        st.session_state.products = [{'id': 0,
                                          'url': None}]

    for product in st.session_state.products:
        if product['url']:
            st.write(product['id'])
        else:
            product_url = get_product_url()
            product['url'] = product_url

    if st.button('Add Product'):
        st.session_state.products.append({'id': len(st.session_state.products),
                                          'url': None})
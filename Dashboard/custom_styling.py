"""Contains custom styling for Dashboard."""

import logging

import streamlit as st

def apply_custom_styling() -> None:
    """Creates the custom styling for streamlit."""
    logging.info('Apply custom CS styling.')
    st.markdown('''
<head>
    <style>
        :root {
            --orange: #DA884A;
            --dorange: #E0935A;
            --slate: #4E5B6A;
        }
        
        .pageTitle {
            color: var(--orange);
        }
                
        [data-testid="stHeader"] {
            background-color: var(--slate);
        }

        [data-testid="stSidebarContent"] {
            background-color: var(--slate);
        }

        [data-testid="stSidebarNavLink"] > span {
            color: white;
        }               

        header[data-testid="stHeader"] {
            height: 5rem;
        }
        
        div[data-testid="stSidebarContent"]{
            overflow: visible;
        }

        img[data-testid="stLogo"] {
            height: 2.2rem;
            width:  22rem;
            max-width: 22rem;
            z-index: 9999999;
        }
        
        div[data-testid="collapsedControl"]{
            overflow: visible;
            width: 400px;
            right: 50px;
        }
                
        a[data-testId="stPageLink-NavLink"] p{
            color: white;
        }
        
        button[data-testid="baseButton-secondary"]{
            background-color: var(--orange);
            color: white;
        }
        
        [data-testid="stSidebarUserContent"] [data-testid="stAlert"] .st-emotion-cache-d4qd9r p{
            color: white;
        }
    
        button[data-testid="baseButton-primaryFormSubmit"] {
            background-color: var(--orange);
            border: 1px solid var(--orange);
        }
        
        button[data-testid="baseButton-primaryFormSubmit"]:hover {
            background-color: var(--dorange);
            border: 1px solid var(--dorange);
        }
        
        button[data-testid="baseButton-primary"] {
            background-color: var(--orange);
            border: 1px solid var(--orange);
        }
        
        button[data-testid="baseButton-primary"]:hover {
            background-color: var(--dorange);
            border: 1px solid var(--dorange);
        }

        button[data-testid="baseButton-secondary"] {
            background-color: var(--orange);
            border: 1px solid var(--orange);
        }
        
        button[data-testid="baseButton-secondary"]:hover {
            background-color: var(--dorange);
            border: 1px solid var(--dorange);
            color: white;
        }
                
                

        a[data-testid="baseLinkButton-secondary"] {
            background-color: var(--orange);
            border: 1px solid var(--orange);
        }
        
        a[data-testid="baseLinkButton-secondary"] p {
            color: white;
        }
        
        a[data-testid="baseLinkButton-secondary"]:hover {
            background-color: var(--dorange);
            border: 1px solid var(--dorange);
            color: white;
        }
                
    

        a[data-testid="baseButton-secondary"] {
            background-color: var(--orange);
            border: 1px solid var(--orange);
        }
        
        a[data-testid="baseButton-secondary"] p {
            color: white;
        }
        
        .st-emotion-cache-1s0tdct:focus:not(:active) {
            background-color: var(--dorange);
            border: 1px solid var(--dorange);
            color: white;
        }                

        div[data-testid="stExpander"] summary div[data-testid="stMarkdownContainer"] > p > strong {
            font-size:1.2rem;
        }
    </style>
</head>
''', unsafe_allow_html=True)

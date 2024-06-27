import streamlit as st

def apply_custom_styling() -> None:
    st.markdown('''
<head>
    <style>
        :root {
            --orange: #DA884A;
            --slate: #4E5B6A;
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

    </style>
</head>
''', unsafe_allow_html=True)
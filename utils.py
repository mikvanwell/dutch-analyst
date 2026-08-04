import streamlit as st


def load_css():
    st.markdown("""
        <style>

        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

        html,
        body,
        [class*="st-"],
        .stMarkdown,
        .stText,
        .stDataFrame,
        .stButton,
        .stSelectbox,
        .stRadio {
            font-family: 'DM Sans', sans-serif;
        }

        h1,
        h2,
        h3,
        h4,
        h5,
        h6 {
            font-family: 'DM Sans', sans-serif;
        }

        </style>
    """, unsafe_allow_html=True)
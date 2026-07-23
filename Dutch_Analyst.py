import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠"
)

st.title("Eredivisie Analyst")
st.write("**Welcome to *the* app with everything you need to analyse Eredivisie football.**")

st.write("Wondering how the Eredivisie would look based on expected goals?")
st.page_link("pages/Expected_Standings.py", label="➡️ Go to Expected Standings 📊")

st.write("Do you need help with your Fantasy Eredivisie squad?")
st.page_link("pages/Fantasy_Eredivisie.py", label="➡️ Go to our Fantasy Hub 🔮")

st.write("**(Coming soon)** Want to know which players are performing well?")
st.page_link("pages/Player_Analysis.py", label="➡️ Go to Player Analysis ⚽️")

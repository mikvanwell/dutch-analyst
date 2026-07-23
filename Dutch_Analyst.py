import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠"
)

st.title("Dutch Analyst")
st.write("**Welcome to *the* app with everything you need to analyse Dutch football.**")

st.write("Wondering which Eredivisie teams have the best underlying data?")
st.page_link("pages/Expected_Standings.py", label="➡️ Go to Expected Standings 📊")

st.write("Do you need help with your Fantasy Eredivisie squad?")
st.page_link("pages/Fantasy_Eredivisie.py", label="➡️ Go to our Fantasy Hub 🔮")

st.write("**(Coming soon)** Want to know which players are performing well?")
st.page_link("pages/Player_Analysis.py", label="➡️ Go to Player Analysis ⚽️")

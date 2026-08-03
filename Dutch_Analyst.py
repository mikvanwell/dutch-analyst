import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="🏠"
)

st.title("Dutch Analyst")
st.write("**Welcome to the site with everything you need to analyse Dutch football and optimize your *Fantasy Voetbal* squad.**")

st.write("Wondering which Eredivisie teams have the best underlying data?")
st.page_link("pages/Team_Data.py", label="➡️ Go to Team Data 📊")

st.write("Do you need help with your Fantasy Eredivisie squad?")
st.page_link("pages/FDR_Schedule.py", label="➡️ Go to our Fantasy Hub 🔮")

st.write("Want to know which players are expected to score most points?")
st.page_link("pages/Player_Analysis.py", label="➡️ Go to Player Analysis ⚽️")

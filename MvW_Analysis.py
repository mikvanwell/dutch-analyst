import streamlit as st
from utils import load_css

st.set_page_config(
    page_title="Home",
    page_icon="🏠"
)

load_css()

st.title("Mik van Well Analysis")

st.write("**Welcome to the site with everything you need to analyse Eredivisie football and optimize your *Fantasy Voetbal* squad.**")

st.write("Wondering which teams have the best underlying data?")
st.page_link("pages/1_Team_Data.py", label="➡️ Go to Team Data 📊")

st.write("Curious which teams face the easiest schedule?")
st.page_link("pages/2_FDR_Schedule.py", label="➡️ Go to our Fantasy Schedule 🔮")

st.write("Want to know which players are expected to score most points?")
st.page_link("pages/3_Player_Analysis.py", label="➡️ Go to Player Analysis ⚽️")

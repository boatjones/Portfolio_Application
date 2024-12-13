import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import streamlit.components as components
import pygwalker as pyg

# Adjust the width of the Streamlit page
st.set_page_config(page_title="Use Pygwalker In Streamlit", layout="wide")

# imports of my external files
sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_postgres import PgHook

# make database helper object
db = PgHook()

# check for user authentication
if not st.session_state.authentication_status:
    st.info("Please Login from the Home page and try again.")
    st.stop()
st.write(f'Welcome *{st.session_state["name"]}*')

# Add Title
st.title("Use Pygwalker In Streamlit")

# monte carlo selections
sql = "select sector_name from sector where sector_id != 8"
sect_name = db.alc_query(sql)
answer = st.selectbox(
    "Select an industry sector to chart:",
    options=sorted(sect_name["sector_name"].tolist()),
)
if st.button("View Monte Carlo Results for Sector"):
    try:
        ##### Determine Returns Dataframe Based on User Choice
        if answer == "All Sectors":
            sql = "select * from mc_all"
            print(f"all sector sql: {sql}")
            df = db.alc_query(sql)
        else:
            # get table belonging to that sector
            sql = f"select mc_table from sector where sector_name = '{answer}'"
            mc_df = db.alc_query(sql)
            # get appropriate table to use for charting
            mc_table = mc_df["mc_table"].iloc[0]
            sql = f"select * from {mc_table}"
            print(f"Specific sector sql: {sql}")
            df = db.alc_query(sql)

        # Generate the HTML using Pygwalker
        pyg_html = pyg.to_html(df)

        # Embed the HTML into the Streamlit app
        components.v1.html(pyg_html, height=1000, scrolling=True)

    except:
        st.error("Database or other error")

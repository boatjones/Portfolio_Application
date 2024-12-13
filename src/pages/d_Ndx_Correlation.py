import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import plotly.express as px  # plotly still uncooperative
import matplotlib.pyplot as plt
import seaborn as sns


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

st.title("View Sector Indices Against Commodity")

if st.button("View Sector Index Returns"):
    try:
        ###### get the index data
        sql = "select price_date, all_sect, ep, ref_mkt, equip, int, coal, bas_mat, comm from ndx_vals"
        # print(f"all sector sql: {sql}")
        df = db.alc_query(sql)
        ### also get dataframe for a descriptive legend
        sql2 = "select upper(ndx_name) as abbreviation, sector_name from sector where sector_id != 8"
        df_descriptions = db.alc_query(sql2)
        ###### Chart the Returns
        fig, ax = plt.subplots(figsize=(12, 6))
        for column in df.columns:
            if column != "price_date":
                if column == "comm":
                    ax.plot(
                        df["price_date"],
                        df[column],
                        label=column.upper(),
                        linewidth=2,
                        color="black",
                    )
                else:
                    ax.plot(df["price_date"], df[column], label=column.upper())

        plt.ylabel("Price Start @ 100")
        plt.xlabel("Date")
        plt.title("Portfolio Sector Performance Against Commodity")
        plt.grid(axis="y")
        plt.legend()
        st.pyplot(fig)
        st.subheader("Sector Descriptions")
        st.write(df_descriptions)
    except:
        st.error("Database Error")

if st.button("View Correlation Matrix of Sectors & Commodity"):
    try:
        #### get the index values
        sql = "select price_date, all_sect, ep, ref_mkt, equip, int, coal, bas_mat, comm from ndx_vals"
        # print(f"all sector sql: {sql}")
        df = db.alc_query(sql)
        ### also get dataframe for a descriptive legend
        sql2 = "select upper(ndx_name) as abbreviation, sector_name from sector where sector_id != 8"
        df_descriptions = db.alc_query(sql2)
        #### calculate the correlations
        # first drop price_date (included in SQL to prevent any sneaky select distincts)
        df = df.drop(columns=["price_date"])
        corr = df.corr()
        #### chart the correlation matrix
        fig = plt.figure(figsize=(8, 6))
        mask = np.zeros_like(corr)  # fills with zeros
        mask[np.triu_indices_from(mask)] = True
        plt.title("Heatmap of Portfolio Sector and Commodity Correlations")
        sns.heatmap(corr, vmin=-1, vmax=1, cmap="coolwarm", annot=True, mask=mask)
        st.pyplot(fig)
        st.subheader("Sector Descriptions")
        st.write(df_descriptions)
    except:
        st.error("Database error")

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import plotly.express as px  # plotly still uncooperative
import matplotlib.pyplot as plt

# imports of my external files
sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_postgres import PgHook
import mc_core

# make database helper object
db = PgHook()

# check for use authentication
if not st.session_state.authentication_status:
    st.info("Please Login from the Home page and try again.")
    st.stop()
st.write(f'Welcome *{st.session_state["name"]}*')

st.title("Monte Carlo Simulation & Index Construction")
if st.button("Run Monte Carlo Simulations for Portfolio Segments & Compute Indices"):
    try:
        # get sector table and fields that drive indices name and monte carlo table name
        sql = "select sector_id, sector_name, mc_table, ndx_name from sector order by sector_id"
        sector_df = db.alc_query(sql)

        first = True
        for _, row in sector_df.iterrows():
            sector_id = row["sector_id"]
            sector_name = row["sector_name"]
            mc_table = row["mc_table"]
            ndx_name = row["ndx_name"]

            if sector_id == 0:
                sql = "select db_name from portfolio where sector_id <> 7"
            else:
                sql = f"select db_name from portfolio where sector_id = {sector_id}"
            # get tickers for portfolio
            df = db.alc_query(sql)
            # turn into a list
            port_list = df["db_name"].tolist()
            # use this list to run through the external Monte Carlo function
            mc_df = mc_core.mc_hammer(port_list)
            # save results to a table
            tablename = mc_table
            db.alc_df_2_db(mc_df, tablename)
            st.success(f"{sector_name} Calculated and Saved to Database")
            # calculate the index value on optimal weighting found
            if first:
                # put first index into ndx_vals dataframe
                ndx_vals = mc_core.ndx_calc(mc_df)
                ndx_vals.rename(columns={"portfolio_value": ndx_name}, inplace=True)
                first = False
            else:
                # calc successive indices in their own dataframes
                new_ndx = mc_core.ndx_calc(mc_df)
                new_ndx.rename(columns={"portfolio_value": ndx_name}, inplace=True)
                # ... and then join them into the ndx_vals dataframe
                ndx_vals = pd.merge(
                    ndx_vals,
                    new_ndx[["price_date", ndx_name]],
                    on="price_date",
                    how="left",
                )
            st.success(f"Index calculated for {sector_name}")

        # Write index table to database
        tablename = "ndx_vals"
        db.alc_df_2_db(ndx_vals, tablename)
        st.success("Index table 'ndx_vals' written to database")

    except:
        st.error("Error in Database or process")

sql = "select sector_name from sector"
sect_name = db.alc_query(sql)
answer = st.selectbox(
    "Select an industry sector to chart:",
    options=sorted(sect_name["sector_name"].tolist()),
)
if st.button("View Monte Carlo Results for Sector"):
    try:
        ##### Determine Returns Dataframe Based on User Choice
        if answer == "All Sectors":
            sql = "select return, volatility, sharpe from mc_all"
            print(f"all sector sql: {sql}")
            df = db.alc_query(sql)
        else:
            # get table belonging to that sector
            sql = f"select mc_table from sector where sector_name = '{answer}'"
            mc_df = db.alc_query(sql)
            # get appropriate table to use for charting
            mc_table = mc_df["mc_table"].iloc[0]
            sql = f"select return, volatility, sharpe from {mc_table}"
            print(f"Specific sector sql: {sql}")
            df = db.alc_query(sql)

        # plot simulation results
        fig = plt.figure(figsize=(12, 6))
        plt.scatter(df["volatility"], df["return"], c=df["sharpe"])
        plt.colorbar(label="Sharpe Ratio")
        # plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = False
        # plt.rcParams['ytick.left'] = plt.rcParams['ytick.labelleft'] = True
        plt.xlabel("Volatility")
        plt.ylabel("Returns")
        plt.title("Monte Carlo Simulation Results")
        st.pyplot(fig)

    except:
        st.error("Database or other error")

# button to compute the simulations & store to db tables
# take top record from each sim and construct index & compute price starting @ 100 and log returns
# write out to indices table
# have progress text showing where it is
# selectbox & button to view chart of simulation results for each segment & portfolio pulling from tables

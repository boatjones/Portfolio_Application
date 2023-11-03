import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
import plotly.express as px  # plotly still uncooperative
import matplotlib.pyplot as plt

# Dead imports
# from datetime import datetime
# from dateutil.relativedelta import relativedelta
# import yfinance as yf

# imports of my external files
sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_postgres import PgHook
import mc_core

# make database helper object
db = PgHook()

st.title("Monte Carlo Simulation & Index Construction")
if st.button("Run Monte Carlo Simulations for Portfolio Segments & Compute Indices"):
    try:
        # 1) get full portfolio
        sql = "select db_name from portfolio where sector_id <> 7"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_all = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_all"
        db.alc_df_2_db(mc_all, tablename)
        st.success("Full Portfolio Calculated and Saved to Database")
        # calculate index value
        ndx_vals = mc_core.ndx_calc(mc_all)
        ndx_vals.rename(columns={"portfolio_value": "all_sect"}, inplace=True)
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Full Portfolio")

        # 2) get sector 1 Exploration and Production
        sql = "select db_name from portfolio where sector_id = 1"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_ep = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_ep"
        db.alc_df_2_db(mc_ep, tablename)
        st.success("Exploration & Production Port Calculated and Saved to Database")
        # calculate index value
        ndx_ep = mc_core.ndx_calc(mc_ep)
        ndx_ep.rename(columns={"portfolio_value": "ep"}, inplace=True)
        # merge ep column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals, ndx_ep[["price_date", "ep"]], on="price_date", how="left"
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Exploration & Production")

        # 3) get sector 2 Refining and Marketing
        sql = "select db_name from portfolio where sector_id = 2"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_refmkt = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_refmkt"
        db.alc_df_2_db(mc_refmkt, tablename)
        st.success("Refining & Marketing Port Calculated and Saved to Database")
        # calculate index value
        ndx_refmkt = mc_core.ndx_calc(mc_refmkt)
        ndx_refmkt.rename(columns={"portfolio_value": "ref_mkt"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals, ndx_refmkt[["price_date", "ref_mkt"]], on="price_date", how="left"
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Refining & Marketing")

        # 4) get sector 3 Equipment and Services
        sql = "select db_name from portfolio where sector_id = 3"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_equip = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_equip"
        db.alc_df_2_db(mc_equip, tablename)
        st.success("Equipment & Services Port Calculated and Saved to Database")
        # calculate index value
        ndx_equip = mc_core.ndx_calc(mc_equip)
        ndx_equip.rename(columns={"portfolio_value": "equip"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals, ndx_equip[["price_date", "equip"]], on="price_date", how="left"
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Equipment & Services")

        # 5) get sector 4 Integrated
        sql = "select db_name from portfolio where sector_id = 4"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_int = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_int"
        db.alc_df_2_db(mc_int, tablename)
        st.success("Integrated Port Calculated and Saved to Database")
        # calculate index value
        ndx_int = mc_core.ndx_calc(mc_int)
        ndx_int.rename(columns={"portfolio_value": "int"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals, ndx_int[["price_date", "int"]], on="price_date", how="left"
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Integrated")

        # 6: get sector 5 Thermal Coal
        sql = "select db_name from portfolio where sector_id = 5"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_coal = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_coal"
        db.alc_df_2_db(mc_coal, tablename)
        st.success("Thermal Coal Port Calculated and Saved to Database")
        # calculate index value
        ndx_coal = mc_core.ndx_calc(mc_coal)
        ndx_coal.rename(columns={"portfolio_value": "coal"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals, ndx_coal[["price_date", "coal"]], on="price_date", how="left"
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Thermal Coal")

        # 7: get sector 6 Basic Materials
        sql = "select db_name from portfolio where sector_id = 6"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_bas_mat = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_bas_mat"
        db.alc_df_2_db(mc_bas_mat, tablename)
        st.success("Basic Materials Port Calculated and Saved to Database")
        # calculate index value
        ndx_bas_mat = mc_core.ndx_calc(mc_bas_mat)
        ndx_bas_mat.rename(columns={"portfolio_value": "bas_mat"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals,
            ndx_bas_mat[["price_date", "bas_mat"]],
            on="price_date",
            how="left",
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Basic Materials")

        # 8: get sector 7 Commodity
        sql = "select db_name from portfolio where sector_id = 7"
        df = db.alc_query(sql)
        port_list = df["db_name"].tolist()
        # run simulation on selection
        mc_comm = mc_core.mc_hammer(port_list)
        # save results to database
        # create table in Postgres
        tablename = "mc_comm"
        db.alc_df_2_db(mc_comm, tablename)
        st.success("Commodity Port Calculated and Saved to Database")
        # calculate index value
        ndx_comm = mc_core.ndx_calc(mc_comm)
        ndx_comm.rename(columns={"portfolio_value": "comm"}, inplace=True)
        # merge new column in to main index dataframe
        ndx_vals = pd.merge(
            ndx_vals,
            ndx_comm[["price_date", "comm"]],
            on="price_date",
            how="left",
        )
        # ndx_vals.to_excel("test.xlsx")
        st.success("Index calculated for Commodity")

        # 9: write index table to database
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

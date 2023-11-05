import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from datetime import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import plotly.express as px  # plotly still uncooperative
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(Path(__file__).parents[1]))
from to_postgres import PgHook

# make database helper object
db = PgHook()

st.title("Individual Historical Prices")

if st.button("Show Portfolio and Sectors"):
    try:
        sql = """select p.ticker,
                        p.security_name,
                        s.sector_name
                from portfolio p, sector s
                where s.sector_id = p.sector_id
            """
        df = db.alc_query(sql)
        st.write(df)
    except:
        st.error("Database Error")

if st.button("Get/Refresh Prices & Compute Log Returns"):
    try:
        # find dates for import
        today = datetime.today().strftime("%Y-%m-%d")
        beg_date = (datetime.today() - relativedelta(years=20)).strftime("%Y-%m-%d")
        # get list of tickers from database to work with
        sql = "select ticker from portfolio"
        df = db.alc_query(sql)
        port_list = df["ticker"].tolist()

        # create class to convert string to object location name
        class ClassThing:
            def __init__(self, name):
                self.name = name

        ##### Stock Downloading Section
        # dictionary to hold ticker and pd.series object location name
        dct = {name: ClassThing(name) for name in port_list}
        # get price data for tickers in list using yfinance where pd.series are memory location names
        for stk in port_list:
            print(f"Downloading data for {stk}")
            dct[stk] = yf.download(stk, start=beg_date, end=today)["Adj Close"]
        # combine the tickers into a single dataframe
        port = pd.concat([dct[x] for x in port_list], axis=1)

        ###### Write Prices To Database
        # get listing of fields
        port.columns = port_list
        # convert columns to lower prior to load - Postgres is strict
        port.columns = port.columns.str.lower()
        # replace "=" in tickers with "_"
        port.columns = port.columns.str.replace("=", "_")
        # rename 'date' index field to 'price_date' to not piss off Postgres
        port = port.rename_axis("price_date")
        # create table in Postgres
        tablename = "prices"
        db.alc_df_2_db(port, tablename)
        st.success("Data retrieved and saved to prices table")

        ###### Compute Log Returns and Save to Database
        # prepare dataframe to compute returns
        port.fillna(0, inplace=True)
        port.iloc[:, 1:] = port.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
        # compute log returns
        log_rets = np.log(port / port.shift(1))
        # drop first row
        log_rets = log_rets.drop(log_rets.index[0])  # replaced by one line below
        # fill any remaining nulls with zero
        log_rets = log_rets.fillna(0)  # replaced by one line below
        # log_rets = log_rets.dropna() <== this was too brutal and truncated years of data restoring previous 2 lines
        # Find and replace infinite values with zero
        log_rets.replace([np.inf, -np.inf], np.nan, inplace=True)
        log_rets.fillna(0, inplace=True)
        # create table in Postgres
        tablename = "log_returns"
        db.alc_df_2_db(log_rets, tablename)
        st.success("Log returns calculated and saved to log_returns table")

    except:
        st.error("Error in connecting to database or yfinance")

sql = "select sector_name from sector"
sect_name = db.alc_query(sql)
answer = st.selectbox(
    "Select an industry sector to chart:",
    options=sorted(sect_name["sector_name"].tolist()),
)
if st.button("View Sector Returns"):
    try:
        ##### Determine Returns Dataframe Based on User Choice
        if answer == "All Sectors":
            sql = "select * from log_returns"
            print(f"all sector sql: {sql}")
            df = db.alc_query(sql)
            # get dataframe for descriptive text
            sql3 = "select ticker, security_name from portfolio"
            df_descriptions = db.alc_query(sql3)
        else:
            # get tickers belonging to that sector - use lowercased & replaced fieldnames
            sql = f"select p.ticker from portfolio p, sector s where s.sector_id = p.sector_id and s.sector_name = '{answer}'"
            print(f"ticker select: {sql}")
            ticker_df = db.alc_query(sql)
            # make tickers a list
            # first lowercasing them
            ticker_lst = [ticker.lower() for ticker in ticker_df["ticker"]]
            # then replacing any "=" characters
            ticker_lst = [ticker.replace("=", "_") for ticker in ticker_lst]
            # put them in a comma separated string
            columns = ", ".join(ticker_lst)
            # use this to select just these tickers from table
            sql2 = f"select price_date, {columns} from log_returns"
            print(f"df select: {sql2}")
            df = db.alc_query(sql2)
            # also get a dataframe for descriptive text
            sql3 = f"select p.ticker, p.security_name from portfolio p, sector s where s.sector_id = p.sector_id and  s.sector_name = '{answer}'"
            df_descriptions = db.alc_query(sql3)

        ###### Cumulative Return Calculation
        # Select numeric columns for log returns excluding the 'date' column
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        # Compute cumulative sum for the numeric columns
        cumul_return2 = df[numeric_columns].cumsum()
        # merge the price_date column back with the cumulative log returns
        cumul_return2.insert(0, "price_date", df["price_date"])

        ###### Chart the Returns
        fig = plt.figure(figsize=(12, 6))
        for column in cumul_return2.columns:
            if column != "price_date":
                plt.plot(
                    cumul_return2["price_date"],
                    cumul_return2[column] * 100,
                    label=column.upper(),
                )

        plt.ylabel("Returns")
        plt.xlabel("Date")
        plt.title("Individual Percent Log Returns")
        plt.legend()
        plt.grid(axis="y")
        st.pyplot(fig)
        st.subheader("Security Descriptions")
        st.write(df_descriptions)

    except:
        st.error("Database error")

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

if st.button("Get and Refresh Prices"):
    try:
        # find dates for import
        today = datetime.today().strftime("%Y-%m-%d")
        five = (datetime.today() - relativedelta(years=5)).strftime("%Y-%m-%d")
        sql = "select ticker from portfolio"
        df = db.alc_query(sql)
        port_list = df["ticker"].tolist()

        # create class to convert string to object location name
        class ClassThing:
            def __init__(self, name):
                self.name = name

        # dictionary to hold ticker and pd.series object location name
        dct = {name: ClassThing(name) for name in port_list}
        # get price data for tickers in list using yfinance where pd.series are memory location names
        for stk in port_list:
            print(f"Downloading data for {stk}")
            dct[stk] = yf.download(stk, start=five, end=today)["Adj Close"]
        # combine the tickers into a single dataframe
        port = pd.concat([dct[x] for x in port_list], axis=1)
        # ticker names to portfolio
        port.columns = port_list
        # convert columns to lower prior to load - Postgres is strict
        port.columns = port.columns.str.lower()
        # port.index.name = port.index.name.lower()
        port = port.rename_axis("price_date")
        tablename = "prices"
        db.alc_df_2_db(port, tablename)
        # port.to_csv("test_port.csv")
        st.success("Data retrieved and saved to prices table")
        # prepare dataframe to compute returns
        port.fillna(0, inplace=True)
        port.iloc[:, 1:] = port.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
        # compute log returns
        log_rets = np.log(port / port.shift(1))
        # drop first row
        log_rets = log_rets.drop(log_rets.index[0])
        # fill any remaining nulls with zero
        log_rets = log_rets.fillna(0)
        tablename = "log_returns"
        db.alc_df_2_db(log_rets, tablename)

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
        # determine returns dataframe based on user choice
        if answer == "All Sectors":
            sql = "select * from log_returns"
            print(f"all sector sql: {sql}")
            df = db.alc_query(sql)
        else:
            # get tickers belonging to that sector
            sql = f"select p.ticker from portfolio p, sector s where s.sector_id = p.sector_id and s.sector_name = '{answer}'"
            print(f"ticker select: {sql}")
            ticker_df = db.alc_query(sql)
            # make tickers a list
            ticker_lst = [ticker.lower() for ticker in ticker_df["ticker"]]
            # put them in a comma separated string
            columns = ", ".join(ticker_lst)
            # use this to select just these tickers from table
            sql2 = f"select price_date, {columns} from log_returns"
            print(f"df select: {sql2}")
            df = db.alc_query(sql2)
            st.dataframe(df)
            df.to_csv("test_out.csv")

        # calculate cumulative return data
        cumul_return2 = (
            df.drop(columns=["price_date"]).apply(lambda x: (1 + x).cumprod() - 1) * 100
        )
        cumul_return2.insert(0, "price_date", df["price_date"])

        # chart the returns
        fig = plt.figure(figsize=(12, 6))
        for column in cumul_return2.columns:
            if column != "price_date":
                plt.plot(
                    cumul_return2["price_date"],
                    cumul_return2[column],
                    label=column.upper(),
                )

        plt.ylabel("Returns")
        plt.xlabel("Date")
        plt.title("Individual Percent Returns")
        plt.legend()
        st.pyplot(fig)

    except:
        st.error("Database error")

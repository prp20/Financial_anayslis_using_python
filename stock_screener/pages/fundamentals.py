import streamlit as st
import time
import pandas as pd
import yfinance as yf
import numpy as np
import requests
from time import sleep
import datetime as dt
import plotly.express as px


def get_pandl_data(ticker):
    data = requests.get(f"http://localhost:8000/profitloss/{ticker}/").json()
    new_data = pd.json_normalize(data)
    return new_data


def get_balance_sheet_data(ticker):
    data = requests.get(
        f"http://localhost:8000/balance_sheet/{ticker}/").json()
    new_data = pd.json_normalize(data)
    return new_data


st.set_page_config(page_title="Fundamentals Of Stock Data", layout="wide")
st.markdown("# Fundamentals Of Stock Data")
st.sidebar.header("Fundamentals Of Stock Data")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)
ticker = st.sidebar.text_input('Ticker', "INFY")

start_date = st.sidebar.date_input('Start Date', dt.date(2023, 1, 1))
end_date = st.sidebar.date_input('End Date')
end_date = dt.datetime.now() if not end_date else end_date

stock_data = yf.download(f"{ticker}.NS", start=start_date, end=end_date)
fig = px.line(stock_data, x=stock_data.index,
              y=stock_data['Adj Close'], title=ticker)
st.plotly_chart(fig)
pandl_sheet = get_pandl_data(ticker)
balance_sheet = get_balance_sheet_data(ticker)
st.header(f"Profit and Loss for Stock {ticker}")
st.write(pandl_sheet)

st.header(f"Balance Sheet for Stock {ticker}")
st.write(balance_sheet)

import streamlit as st
import time
import pandas as pd
import yfinance as yf
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from time import sleep
import datetime as dt
import plotly.express as px


def get_number_from_percentage(li):
    num_span = li.find('span', {'class': 'number'})
    num_span = num_span.text.replace(',', '')
    return float(num_span) if (num_span != '') else 0.0


def get_cols(html_val):
    cols = ['Columns Name']
    col_name = html_val.find("table").find("thead").find_all("tr")
    val_list = col_name[0].get_text().split("\n")
    for val in val_list:
        if val != "":
            cols.append(val.split("  ")[-1]
                        ) if val.split("  ")[-1] != "" else None
    return cols


def get_dataframe_from_table(div_html, cols, dataframe):
    col_name = div_html.find("table").find("tbody").find_all("tr")
    rows = div_html.find("table").find("tbody").find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        data = {}
        data[cols[0]] = cells[0].get_text().split("\n")[2]
        for idx, col in enumerate(cols[1:]):
            text_val = cells[idx+1].get_text().split("\n")
            if text_val[1]:
                if "%" not in text_val[1] and "\n" not in text_val[1]:
                    text_val[1] = float(text_val[1].replace(",", ""))
                else:
                    text_val[1] = float(text_val[1].replace("%", ""))
            data[col] = text_val[1]
        dataframe = pd.concat(
            [dataframe, pd.DataFrame([data])], ignore_index=True)
    return dataframe


def load_page(link):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(link, headers=hdr)
    page = urlopen(req)
    soup = BeautifulSoup(page, features='lxml')
    return soup


def get_pandl_data(ticker):
    div_html = soup.find('section', {'id': 'profit-loss'})
    cols = get_cols(div_html)
    pandl_sheet = pd.DataFrame(columns=cols)
    pandl_sheet = get_dataframe_from_table(div_html, cols, pandl_sheet)
    return pandl_sheet


def get_balance_sheet_data(ticker):
    div_html = soup.find('section', {'id': 'balance-sheet'})
    cols = get_cols(div_html)
    pandl_sheet = pd.DataFrame(columns=cols)
    pandl_sheet = get_dataframe_from_table(div_html, cols, pandl_sheet)
    return pandl_sheet


st.set_page_config(page_title="Fundamentals Of Stock Data", layout="wide")
st.markdown("# Fundamentals Of Stock Data")
st.sidebar.header("Fundamentals Of Stock Data")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)
ticker = st.sidebar.text_input('Ticker', "INFY")
link = f"https://www.screener.in/company/{ticker}/consolidated/"
soup = load_page(link)

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

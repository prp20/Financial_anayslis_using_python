import streamlit as st
import time
import pandas as pd
import requests
from time import sleep

st.set_page_config(page_title="Stock Screener", layout="wide")

st.markdown("# Stock Screener")
st.sidebar.header("Stock Screener")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)


def load_data():
    data = requests.get("http://localhost:8000/stock_screener").json()
    new_data = pd.json_normalize(data)
    return new_data


st.checkbox("Use container width", value=False, key="use_container_width")
with st.spinner('Wait for it...'):
    df = load_data()
    df = df.round({"Market Cap": 2, "Price": 2, "P/E": 2,
                  "Book Value": 2, "ROCE": 2, "ROE": 2, })
st.table(df)
st.success('Done!')


# new_data.drop(['Series', 'ISIN Code'], axis=1, inplace=True)
# st.table(new_data)

# progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")

import streamlit as st
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from time import sleep

cols = ['Company Name', 'Industry', 'Symbol', 'Series', 'ISIN Code',
        'Market Cap', 'Price', 'P/E', 'Book Value', 'ROCE', 'ROE']


def get_number_from_percentage(li):
    num_span = li.find('span', {'class': 'number'})
    num_span = num_span.text.replace(',', '')
    return float(num_span) if (num_span != '') else 0.0


def get_company_fundamentals(SCRIP):
    link = f'https://www.screener.in/company/{SCRIP}/consolidated'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(link, headers=hdr)

    try:
        page = urlopen(req)
        soup = BeautifulSoup(page)

        div_html = soup.find('div', {'class': 'company-ratios'})
        ul_html = div_html.find('ul', {'id': 'top-ratios'})
        company_val = {}
        for li in ul_html.find_all("li"):
            name_span = li.find('span', {'class': 'name'})
            if 'Market Cap' in name_span.text:
                company_val['Market Cap'] = get_number_from_percentage(li)
            elif 'Stock P/E' in name_span.text:
                company_val['P/E'] = get_number_from_percentage(li)
            elif 'ROCE' in name_span.text:
                company_val['ROCE'] = get_number_from_percentage(li)
            elif 'ROE' in name_span.text:
                company_val['ROE'] = get_number_from_percentage(li)
            elif 'Book Value' in name_span.text:
                company_val['Book Value'] = get_number_from_percentage(li)
            elif 'Current Price' in name_span.text:
                company_val['Price'] = get_number_from_percentage(li)
            elif 'High / Low' in name_span.text:
                num_spans = li.find_all('span', {'class': 'number'})
                if (len(num_spans) == 2):
                    high_num = num_spans[0].text.replace(',', '')
                    low_num = num_spans[1].text.replace(',', '')
                    company_val['High'] = float(
                        high_num) if (high_num != '') else 0.0
                    company_val['Low'] = float(
                        low_num) if (low_num != '') else 0.0
        print(f'MARKET CAPITILIZATION - {SCRIP}: {company_val} Cr')

    except:
        print(f'EXCEPTION THROWN: UNABLE TO FETCH DATA FOR {SCRIP}')
        company_val = {}
    return company_val


st.set_page_config(page_title="Stock Screener", layout="wide")

st.markdown("# Stock Screener")
st.sidebar.header("Stock Screener")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)

# progress_bar = st.sidebar.progress(0)
# status_text = st.sidebar.empty()
# last_rows = np.random.randn(1, 1)
# chart = st.line_chart(last_rows)
# nifty_data = pd.read_csv('ind_nifty100list.csv')
# cols = list(nifty_data.columns)
# new_data = pd.DataFrame(columns=list(nifty_data.columns))
# for index, row in nifty_data.iterrows():
#     status_text.text("%i%% Complete" % index)
#     new_dict = get_company_fundamentals(row.Symbol)
#     new_dict['Company Name'] = row['Company Name']
#     new_dict['Industry'] = row['Industry']
#     new_dict['Symbol'] = row['Symbol']
#     new_data = pd.concat(
#         [new_data, pd.DataFrame([new_dict])], ignore_index=True)
#     progress_bar.progress(index)
#     sleep(2)


def load_data():
    new_data = pd.read_csv('ratio_nifty100.csv')
    new_data.dropna(how='all', axis=1, inplace=True)
    new_data.drop(columns=new_data.columns[0], axis=1,  inplace=True)
    return new_data


st.checkbox("Use container width", value=False, key="use_container_width")
df = load_data()
st.table(df)

# new_data.drop(['Series', 'ISIN Code'], axis=1, inplace=True)
# st.table(new_data)

# progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.
st.button("Re-run")

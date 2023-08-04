from fastapi import FastAPI, Response
import time
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from time import sleep

app = FastAPI()

cols = ['Company Name', 'Industry', 'Symbol',
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
                company_val['Market Cap'] = round(
                    get_number_from_percentage(li), 2)
            elif 'Stock P/E' in name_span.text:
                company_val['P/E'] = round(get_number_from_percentage(li), 2)
            elif 'ROCE' in name_span.text:
                company_val['ROCE'] = round(get_number_from_percentage(li), 2)
            elif 'ROE' in name_span.text:
                company_val['ROE'] = round(get_number_from_percentage(li), 2)
            elif 'Book Value' in name_span.text:
                company_val['Book Value'] = round(
                    get_number_from_percentage(li), 2)
            elif 'Current Price' in name_span.text:
                company_val['Price'] = round(get_number_from_percentage(li), 2)
        print(f'MARKET CAPITILIZATION - {SCRIP}: {company_val} Cr')

    except:
        print(f'EXCEPTION THROWN: UNABLE TO FETCH DATA FOR {SCRIP}')
        company_val = {}
    return company_val


def load_data():
    new_data = pd.read_csv('ratio_nifty100.csv')
    new_data.dropna(how='all', axis=1, inplace=True)
    new_data.drop(columns=new_data.columns[0], axis=1,  inplace=True)
    return new_data


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


def get_pandl_data(link):
    soup = load_page(link)
    div_html = soup.find('section', {'id': 'profit-loss'})
    cols = get_cols(div_html)
    pandl_sheet = pd.DataFrame(columns=cols)
    pandl_sheet = get_dataframe_from_table(div_html, cols, pandl_sheet)
    return pandl_sheet


def get_balance_sheet_data(link):
    soup = load_page(link)
    div_html = soup.find('section', {'id': 'balance-sheet'})
    cols = get_cols(div_html)
    pandl_sheet = pd.DataFrame(columns=cols)
    pandl_sheet = get_dataframe_from_table(div_html, cols, pandl_sheet)
    return pandl_sheet


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/stock_screener")
async def get_stock_data():
    nifty_data = pd.read_csv('../ind_nifty100list.csv')
    nifty_data.drop(["Series", "ISIN Code"], axis=1, inplace=True)
    cols = list(nifty_data.columns)
    new_data = pd.DataFrame(columns=list(nifty_data.columns))
    for index, row in nifty_data[:20].iterrows():
        new_dict = get_company_fundamentals(row.Symbol)
        new_dict['Company Name'] = row['Company Name']
        new_dict['Industry'] = row['Industry']
        new_dict['Symbol'] = row['Symbol']
        new_data = pd.concat(
            [new_data, pd.DataFrame([new_dict])], ignore_index=True)
        sleep(2)
    return Response(new_data.to_json(orient="records"))


@app.get("/balance_sheet/{ticker}/")
async def get_stock_data(ticker: str):
    print(ticker)
    link = f"https://www.screener.in/company/{ticker}/consolidated/"
    balance_sheet = get_balance_sheet_data(link)
    return Response(balance_sheet.to_json(orient="records"))


@app.get("/profitloss/{ticker}/")
async def get_stock_data(ticker: str):
    print(ticker)
    link = f"https://www.screener.in/company/{ticker}/consolidated/"
    pandl_sheet = get_pandl_data(link)
    return Response(pandl_sheet.to_json(orient="records"))

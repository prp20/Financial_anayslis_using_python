# https://medium.com/@gokhalehemal11/how-to-scrape-financial-websites-using-python-requests-and-beautifulsoup-5f436318ca9

import requests
from bs4 import BeautifulSoup
import time
import csv
import glob
import openpyxl
import pandas as pd


def get_html(url):
    """ Get the HTML of a URL """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # Use lxml parser
    return soup


def create_csv(letter, company_dict):
    """ Create a CSV file for each stock price letter """
    try:
        soup = get_html(
            'https://www.moneycontrol.com/india/stockpricequote/' + letter)
        time.sleep(5)

        links = soup.find_all('a', {'class': 'bl_12'})
        for link in links:
            company_list = []
            company_list.append(link.text)
            company_list.append(link['href'])
            other_urls = scrape_quick_links(link['href'])
            for row in other_urls:
                company_list.append(row['href'])
            company_dict[company_list[0]] = company_list
            print(company_list)
        print("Success for ", letter)

    except Exception as e:
        print("Exception for ", letter, ": ", e)


def print_csv_columns():
    """ Print the contents of all CSVs """
    dataset = pd.DataFrame()
    for filename in glob.glob('stocks/*.csv'):
        data = pd.read_csv(filename, header=None, index_col=False)
        data.drop([0], axis=0, inplace=True)
        data.drop([0], axis = 1, inplace=True)
        data.dropna(inplace=True)
        dataset = pd.concat([dataset, data], ignore_index=True)
        # with open(filename, newline='') as csvfile:
        #     reader = csv.reader(csvfile, delimiter=',')
        #     for row in reader:
        #         if row[0] and row[1] is not None:
        #             print(row[0])
        #             print(row[1], row[2])
        #         else:
        #             continue
    return dataset


def scrape_table(url, stock_name, sheet_name, next_page=False):
    """ Scrape a table from a web page """
    soup = get_html(url)
    table = soup.find('table', {'class': 'mctable1'})
    rows = table.find_all('tr')

    if next_page:
        wb = openpyxl.load_workbook('{}.xlsx'.format(stock_name))
    else:
        wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = sheet_name

    if next_page:
        first_empty_col = sheet.max_column - 2
        for i, row in enumerate(rows):
            for j, el in enumerate(row):
                if j > 2 and j < len(row) - 3:
                    cell_ref = sheet.cell(i + 1, first_empty_col + j + 1)
                    cell_ref.value = el.string
    else:
        for row in rows:
            row_list = [el.string for el in row][:-2]
            sheet.append(row_list)

    wb.save('{}.xlsx'.format(stock_name))


def scrape_quick_links(url):
    """ Scrape quick links from a web page """
    soup = get_html(url)
    quick_links = soup.find('div', {'class': 'quick_links clearfix'})
    links = quick_links.find_all('a')
    return links
    # for link in links:
    #     df[]
    #     print("{} {}".format(link.text, link['href']))

def get_company_name(url):
  soup = get_html(url)
  comp_val = soup.find('div', {'class':'inid_name'})
  return comp_val.text.split("\n")[1]
    
def get_active_href(url):
    """ Get the URL of the active page """
    soup = get_html(url)
    span_tag = soup.find('span', {'class': 'nextpaging'})
    parent_tag = span_tag.find_previous('a')
    if parent_tag:
        href = parent_tag.get('href')
        if href and href != 'javascript:void();':
            return href
    return None


def scrape_table(url, stock_name, sheet_name, next_page=False):
    """ Scrape a table from a web page """
    soup = get_html(url)
    table = soup.find('table', {'class': 'mctable1'})
    rows = table.find_all('tr')

    if next_page:
        wb = openpyxl.load_workbook('{}.xlsx'.format(stock_name))
    else:
        wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = sheet_name

    if next_page:
        first_empty_col = sheet.max_column - 2
        for i, row in enumerate(rows):
            for j, el in enumerate(row):
                if j > 2 and j < len(row) - 3:
                    cell_ref = sheet.cell(i + 1, first_empty_col + j + 1)
                    cell_ref.value = el.string
    else:
        for row in rows:
            row_list = [el.string for el in row][:-2]
            sheet.append(row_list)

    wb.save('{}.xlsx'.format(stock_name))


def main():
    """ Get all the stock web links from A-Z available on 
    moneycontrol and store them into 
    csv files alphabetically """
    # # """ Get contents from the generated csv files """
    # dataframe = pd.read_csv('file_name.csv')
    # print(dataframe)
    dataset = print_csv_columns()

    dataset.columns = ['Company Name', 'Company Url']
    print(dataset.head())

    nifty_data = pd.read_csv('ind_nifty100list.csv')
    # new_data = dataset.merge(nifty_data,how='right')
    # temp_data = new_data[new_data['Company Url'].isna()]
    # for index, row in nifty_data.iterrows():
    #     loc = dataset.loc[dataset['Company Name'] == row['Company Name']]
    #     print(row['Company Name'])
    print(dataset[dataset['Company Name']]== "Zensar Technologies Ltd.")
    # """ Read a url for stock and scrape the urls of financial section
    # like Balance Sheet, Profit and Loss and, Quarterly an Yearly results,
    # Cashflow statments, etc. """
    # url = "https://www.moneycontrol.com/india/stockpricequote/refineries/relianceindustries/RI"
    # scrape_quick_links(url)

    # """ Get the financial section data which we want. In this case Balance Sheet of the stock """
    # url = "https://www.moneycontrol.com/financials/relianceindustries/balance-sheetVI/RI#RI"
    # stock_name = "RELIANCE"
    # sheet_name = "Balance Sheet"

    # """ Store all the available data of all years including searching for previous years's data if available
    # and saving them into a excel file with sheet Balance Sheet in this case """
    # scrape_table(url, stock_name, sheet_name)

    # first_entry = True
    # while url:
    #     print(url)
    #     if first_entry:
    #         scrape_table(url, stock_name, sheet_name)
    #         first_entry = False
    #     else:
    #         scrape_table(url, stock_name, sheet_name, True)
    #     url = get_active_href(url)


if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from tqdm import tqdm
import time


def get_html(url):
    """ Get the HTML of a URL """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')  # Use lxml parser
    return soup


def get_company_name(url):
    if url:
        print(url)
        soup = get_html(url)
        return soup.find('div', {'class': 'inid_name'})


def create_csv(letter, company_dict):
    try:
        soup = get_html(
            'https://www.moneycontrol.com/india/stockpricequote/' + letter)
        time.sleep(5)
        links = soup.find_all('a', {'class': 'bl_12'})
        print(len(links))
        links = links[212:]
        for comp in tqdm(links):
            print(comp['href'])
            comp_name = get_company_name(comp['href'])
            comp_name = comp_name.text.split(
                "\n")[1] if comp_name and comp_name.text else np.nan
            if comp_name:
                company_dict[comp_name] = comp['href']
            else:
                continue
        print("Success for ", letter)
    except Exception as e:
        print("Exception for ", letter, ": ", e)


def main():
    for letter in 'N':
        company_dict = {}
        create_csv(letter, company_dict)
        company_df = pd.DataFrame(company_dict.items())
        company_df.columns = ['company', 'url']
        company_df.to_csv(f"stocks/{letter}.csv", mode='a')


if __name__ == '__main__':
    main()

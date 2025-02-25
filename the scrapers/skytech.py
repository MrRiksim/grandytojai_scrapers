import requests
import re
import os
from pandas import DataFrame
from bs4 import BeautifulSoup

session = requests.Session()
url = 'https://www.skytech.lt/hdd-ssd-priedai-ssd-diskai-c-86_85_1407_1408.html?pagesize=500&sand=2'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
session.get(url, headers=headers)
session.get(url, headers=headers)
r = session.get(url, headers=headers)
if r.ok:
    soup = BeautifulSoup(r.content, 'html.parser')
    models = soup.find_all('td', class_='model')
    names = soup.find_all('td', class_='name')
    prices = soup.find_all('strong', string=re.compile("€"))
    print(len(models))
    print(len(names))
    print(len(prices))
    df = DataFrame({'Model': str(a.text).strip(), 'Name': str(b.text).strip(), 'Price': str(c.text).strip()} for a, b, c in zip(models, names, prices))
    df.to_excel(fr"{os.path.dirname(os.path.realpath(__file__))}\..\the data\skytech\skytech.xlsx", sheet_name='sheet1', index=False)
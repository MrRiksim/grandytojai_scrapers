import requests
import re
import os
from pandas import DataFrame
from bs4 import BeautifulSoup

session = requests.Session()
url = 'https://www.skytech.lt/kompiuteriu-komponentai-hdd-ssd-priedai-v-1407.html?sand=2'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
session.get(url, headers=headers)
session.get(url, headers=headers)
s = session.get(url, headers=headers)
if s.ok:
    soup = BeautifulSoup(s.content, 'html.parser')
    category = soup.find('h1').text
    links = []
    print(category)
    for list in soup.find_all('ul', class_='visi-catlist'):
        entries = list.find_all('a')
        links.extend(f"https://www.skytech.lt{a.attrs.get('href')}?pagesize=500&sand=2" for a in entries)
    #print('\n'.join(links))

for link in links:
    session.get(link, headers=headers)
    session.get(link, headers=headers)
    s = session.get(link, headers=headers)
    if s.ok:
        soup = BeautifulSoup(s.content, 'html.parser')
        models = soup.find_all('td', class_='model')
        names = soup.find_all('td', class_='name')
        prices = soup.find_all('strong', string=re.compile("€"))
        subcategory = str(soup.find('h1').text).replace('/', '-')
        """print(subcategory)
        print(len(models))
        print(len(names))
        print(len(prices))"""
        df = DataFrame({'Model': str(a.text).strip(), 'Name': str(b.text).strip(), 'Price': str(c.text).strip()} for a, b, c in zip(models, names, prices))
        df.to_csv(fr"{os.path.dirname(os.path.realpath(__file__))}\..\the data\skytech\{category}\{subcategory}.csv", index=False, encoding='utf-8-sig')
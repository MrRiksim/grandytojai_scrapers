import requests
import re
import os
from pandas import DataFrame
from bs4 import BeautifulSoup

session = requests.Session()
url = 'https://www.skytech.lt/kompiuteriai-komponentai-kompiuteriu-komponentai-v-85.html?sand=2'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

def nextPage(url, models, names, prices):
    session2 = requests.Session()
    session2.get(url, headers=headers)
    session2.get(url, headers=headers)
    s2 = session2.get(url, headers=headers)
    if s2.ok:
        soup = BeautifulSoup(s2.content, 'html.parser')
        moreModels = soup.find_all('td', class_='model')
        moreNames = soup.find_all('td', class_='name')
        morePrices = soup.find_all('strong', string=re.compile("€"))
        if len(moreModels) != len(moreNames) or len(moreNames) != len(morePrices):
            print('Something went wrong with ' + link)
            return
        models.extend(moreModels)
        names.extend(moreNames)
        prices.extend(morePrices)
    else:
        print('Request failed: ' + link)

links = []
s = session.get(url, headers=headers)
if s.ok:
    soup = BeautifulSoup(s.content, 'html.parser')
    categorylinks = []
    for list in soup.find_all('ul', class_='visi-catlist'):
        entries = list.find_all('a')
        categorylinks.extend(f"https://www.skytech.lt{a.attrs.get('href')}?pagesize=500&sand=2&pav=0&grp=0" for a in entries)
else:
        print('Request failed: ' + url)


for c in categorylinks:
    s = session.get(c, headers=headers)
    if s.ok:
        soup = BeautifulSoup(s.content, 'html.parser')
        category = soup.find('h1').text
        h2 = soup.find('h2').text
        b = category == h2
        if (category != h2):
            links.append(s.url)
        else:
            for list in soup.find_all('ul', class_='visi-catlist'):
                entries = list.find_all('a')
                links.extend(f"https://www.skytech.lt{a.attrs.get('href')}?pagesize=500&sand=2&pav=0&grp=0" for a in entries)
    else:
        print('Request failed: ' + c)

for link in links:
    session.get(link, headers=headers)
    session.get(link, headers=headers)
    s = session.get(link, headers=headers)
    if s.ok:
        soup = BeautifulSoup(s.content, 'html.parser')
        models = soup.find_all('td', class_='model')
        names = soup.find_all('td', class_='name')
        prices = soup.find_all('strong', string=re.compile("€"))
        if len(models) != len(names) or len(names) != len(prices):
            print('Something went wrong with ' + link)
            continue
        if len(models) == 500:
            nextPage(link + '&page=2', models, names, prices)
        subcategory = str(soup.find('h1').text).replace('/', '-')
        category = str(soup.find('div', class_="navbar-breadcrumb").find_all('a')[-1].text).replace('/', '-')
        if category == 'Kompiuterių komponentai':
            category = subcategory
        df = DataFrame({'Model': str(a.text).strip(), 'Name': str(b.text).strip(), 'Price': str(c.text).strip()} for a, b, c in zip(models, names, prices))
        df.to_csv(fr"{os.path.dirname(os.path.realpath(__file__))}\..\the data\skytech\{category}\{subcategory}.csv", index=False, encoding='utf-8-sig', sep=';')
        print(category + ' -> ' + subcategory)
        #print(len(models))
        #print(len(names))
        #print(len(prices))
    else:
        print('Request failed: ' + link)
import requests
import re
import os
from pandas import DataFrame
from bs4 import BeautifulSoup
from scrapers.api.api import ApiClient
from scrapers.dataclass.computer_part import ComputerPart 
from scrapers.enums.computer_part_type import ComputerPartType 

session = requests.Session()
url = 'https://www.skytech.lt/kompiuteriai-komponentai-kompiuteriu-komponentai-v-85.html?sand=2'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

api_client = ApiClient()
computer_part_endpoint = "computerParts"

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

        created_count = 0
        updated_count = 0

        for model, name, price in zip(models, names, prices):
            computer_part = ComputerPart(
                barcode=str(model.text).strip(),
                part_name=str(name.text).strip(),
                part_type=ComputerPartType.from_str(category).value[0],
                price=float(str(price.text).strip().replace(' ', '').removesuffix("€"))
            )
            
            try:
                response = api_client.post_data(computer_part_endpoint, computer_part.__dict__)
                if response.status_code == 201:
                    created_count += 1
            except requests.HTTPError as e:
                if e.response.status_code == 409:
                    response = api_client.put_data(computer_part_endpoint, computer_part.__dict__)
                    if response.status_code == 200:
                        updated_count += 1
                else:
                    print(e)
            finally:
                continue
            
        print(category + ' -> ' + subcategory)
        print(f"Newly scrapped parts: {created_count}")
        print(f"Updated scrapped parts: {updated_count}")
    else:
        print('Request failed: ' + link)
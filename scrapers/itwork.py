import requests
import re
from bs4 import BeautifulSoup

from scrapers.api.api import ApiClient
from scrapers.dataclass.computer_part import ComputerPart
from scrapers.enums.computer_part_type import ComputerPartType

api_client = ApiClient()
computer_part_endpoint = "computerParts"
session = requests.Session()
url = 'https://www.itwork.lt/kompiuteriu-komponentai/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

totalCreated = 0
totalUpdated = 0

def collectLinks(bigLinks, bigAmounts, links, amounts):
    for i in range(len(bigLinks)):
        s = session.get(bigLinks[i], headers=headers)
        if s.ok:
            soup = BeautifulSoup(s.content, 'html.parser')
            check = soup.find("body").find('span', class_='ocf-filter-name')
            if check is None or check.text != 'Kaina':
                links.extend([f"{a.find('a').attrs.get('href')}page/1/?limit=200" for a in soup.find_all('div', class_='refine-item')])
                amounts.extend([int(a.find('span', class_='count-badge').text) for a in soup.find_all('div', class_='refine-item')])
            else:
                links.append(f"{bigLinks[i]}page/1/?limit=200")
                amounts.append(bigAmounts[i])
        else:
            print('Request failed: ' + s.url)

def readProducts(url, models, names, prices, imageUrls, partUrls, discounts, pageCount):
    for i in range(1, pageCount + 1):
        if i != 1:
            url = url.replace(f'page/{i-1}', f'page/{i}')
        s = session.get(url, headers=headers)
        if s.ok:
            soup = BeautifulSoup(s.content, 'html.parser')
            models.extend([a.find_all('span')[-1].text for a in soup.find_all('span', class_='stat-2')])
            names.extend([a.text for a in soup.find_all('div', class_='name')])
            prices.extend([a.text for a in soup.find_all('span', {'class':['price-normal', 'price-new']})])
            imageUrls.extend([a.find('img').attrs.get('data-src') for a in soup.find_all('div', class_='image')])
            partUrls.extend([a.find('a').attrs.get('href') for a in soup.find_all('div', class_='name')])
            discounts.extend([True if bool(re.search("-[2-9][0-9] %", str(a))) else False for a in soup.find_all('div', class_='image')])
            category = soup.find('ul', class_='breadcrumb').find_all('li')[-1].find('a').text
        else:
            print('Request failed: ' + s.url)
    return category

def sendParts(models, names, prices, imageUrls, partUrls, discounts, category, totalCreated, totalUpdated):
    created_count = 0
    updated_count = 0
    for model, name, price, imageUrl, partUrl, discount in zip(models, names, prices, imageUrls, partUrls, discounts):
        computer_part = ComputerPart(
            barcode=model.strip(),
            part_name=name.strip(),
            part_type=ComputerPartType.from_str(category).value[0],
            price=float(price.strip().replace(',', '').removesuffix("€")),
            image_url=imageUrl,
            store_url=partUrl,
            store_name='ITwork',
            has_discount=discount
        )
            
        try:
            response = api_client.post_data(computer_part_endpoint, computer_part.__dict__)
            if response.status_code == 201:
                created_count += 1
            if response.status_code == 409:
                response = api_client.put_data(computer_part_endpoint, computer_part.__dict__)
                updated_count += 1
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                response = api_client.put_data(computer_part_endpoint, computer_part.__dict__)
                if response.status_code == 200:
                    updated_count += 1
            else:
                print(e)
        finally:
            continue
            
    print(category)
    print(f"Newly scraped parts: {created_count}")
    print(f"Updated scraped parts: {updated_count}")
    totalCreated += created_count
    totalUpdated += updated_count
    return totalCreated, totalUpdated
#--------------------------------------------------------------------------------------------------
bigLinks = []
bigAmounts = []
s = session.get(url, headers=headers)
if s.ok:
    soup = BeautifulSoup(s.content, 'html.parser')
    bigLinks.extend([a.find('a').attrs.get('href') for a in soup.find_all('div', class_='refine-item')])
    bigAmounts.extend([int(a.find('span', class_='count-badge').text) for a in soup.find_all('div', class_='refine-item')])
else:
    print('Request failed: ' + s.url)

links = []
amounts = []
collectLinks(bigLinks, bigAmounts, links, amounts)
for i in range(len(links)):
    models = []
    names = []
    prices = []
    imageUrls = []
    partUrls = []
    discounts = []
    category = readProducts(links[i], models, names, prices, imageUrls, partUrls, discounts, int(amounts[i]/200) + 1)
    if [len(models), len(names), len(prices), len(imageUrls), len(partUrls), len(discounts)].count(len(models)) != 6:
        print('Something went wrong with ' + links[i])
        continue
    totalCreated, totalUpdated = sendParts(models, names, prices, imageUrls, partUrls, discounts, category, totalCreated, totalUpdated)
print(f"Total newly scraped parts: {totalCreated}")
print(f"Total updated scraped parts: {totalUpdated}")
import requests
import re
import asyncio
import aiohttp
import time
from bs4 import BeautifulSoup, SoupStrainer

from scrapers.dataclass.computer_part import ComputerPart
from scrapers.enums.computer_part_type import ComputerPartType
from scrapers.scrapper import Scrapper
from scrapers.constants.url import BACKEND_BASE_URL_DEV

class ItworkScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.itwork.lt"
        self.starting_url = "https://www.itwork.lt/kompiuteriu-komponentai"
        self.session = requests.Session()
        self.requests_results = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.google.com/", 
            "Accept-Language": "en-US,en;q=0.9",
        }

    @staticmethod
    def getPageCategoriesAndUrls(soup: BeautifulSoup) -> list[tuple[str, str]]:
        categories = []
        for link in soup.find_all('div', class_='refine-item'):
            a_tag = link.find('a')
            span_tag = link.find('span', class_='links-text')
            if a_tag and span_tag:
                href = a_tag.attrs.get('href')
                text = span_tag.get_text(strip=True)
                categories.append((href, text))
        return categories
    
    def getComputerPartData(self, category_item: BeautifulSoup, category: str, ) -> ComputerPart:
        item_title_el = category_item.find('div', class_="product_thumb")
        part_name = item_title_el.find('div', class_="name").find('a').get_text(strip=True)
        part_type = ComputerPartType.from_str(category).value[0]

        price = float(category_item.select_one('div.price').find('span', string=re.compile('€')).get_text().strip().replace(',', '.').removesuffix("€"))
        part_url = f"{self.base_url}{item_title_el.find('div', class_="name").find('a').attrs.get('href')}"
        image_url = f"{self.base_url}{category_item.find('img').attrs.get('src')}"

        stat_block = category_item.find("span", class_="stat-2")
        spans = stat_block.find_all("span")
        barcode = spans[1].get_text().strip()
        
        return ComputerPart(
            barcode=barcode,
            part_name=part_name,
            part_type=part_type,
            price=price,
            image_url=image_url,
            store_url=part_url,
            store_name='ITwork'
        )

    async def main(self):
        session_content = self.session.get(self.starting_url, headers=self.headers)

        print(session_content.status_code)
        
        soup = BeautifulSoup(session_content.content, 'lxml')
        category_links = self.getPageCategoriesAndUrls(soup)

        for link in category_links:
            print(link)

        self.session.close()

        print("------------------------")

        for category in category_links:
            s = self.session.get(f"{category[0]}", headers=self.headers)
            category_items = soup.find_all('div', class_='product-layout')
            computer_parts_data = [self.getComputerPartData(category_item, category[1]) for category_item in category_items]

            for computer_part in computer_parts_data:
                print(computer_part)



        

        


if __name__ == "__main__":
    start = time.time()
    itwork_scrapper = ItworkScrapper()
    asyncio.run(itwork_scrapper.main())
    end = time.time()
    print(f"Seconds {end - start}")

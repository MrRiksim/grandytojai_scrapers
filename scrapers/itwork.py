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
                print(f"Found category: {text}, URL: {href}")  
                categories.append((href, text))
        return categories
    
    # def getComputerPartData(self, category_item: BeautifulSoup, category: str, ) -> ComputerPart:
    #     item_title_el = category_item.find('a')
    #     part_name = item_title_el.attrs.get('title').strip()
    #     part_type = ComputerPartType.from_str(category).value[0]

    #     price = float(category_item.select_one('div.item-price').find('span', string=re.compile('€')).get_text().strip().replace(',', '.').removesuffix("€"))
    #     part_url = f"{self.base_url}{item_title_el.attrs.get('href')}"
    #     image_url = f"{self.base_url}{category_item.find('img').attrs.get('src')}"

    #     if (new_barcode_value := self.bad_barcode_results_dict.get(part_url.split('itemid=')[1].strip())) and (new_barcode_text := new_barcode_value.get('new_barcode')):
    #         barcode = new_barcode_text
    #     else:
    #         barcode = category_item.select_one('span.item-code').get_text().strip()
    #         if barcode.endswith('...'):
    #             barcode = self.getBarcodeOutOfName(barcode, part_name)
        
    #     return ComputerPart(
    #         barcode=barcode,
    #         part_name=part_name,
    #         part_type=part_type,
    #         price=price,
    #         image_url=image_url,
    #         store_url=part_url,
    #         store_name='ITwork'
    #     )

    async def main(self):
        session_content = self.session.get(self.starting_url, headers=self.headers)

        print(session_content.status_code)
        
        soup = BeautifulSoup(session_content.content, 'lxml')
        category_links = self.getPageCategoriesAndUrls(soup)

        for link in category_links:
            print(link)

        print("------------------------")

        session_results = await self.async_api_client._make_requests([f"{category_tuple[0]}" for category_tuple in category_links], self.headers)

        for session_content, category_tuple in zip(session_results, category_links):
            soup = BeautifulSoup(session_content[0], 'lxml')

            if soup.find('div', class_='refine-categories'):
                new_category_links = self.getPageCategoriesAndUrls(soup)
                category_links.extend(new_category_links)
                session_results.extend(await self.async_api_client._make_requests([f"{self.base_url}{category_tuple_new[0]}" for category_tuple_new in new_category_links], self.headers))
                continue
            
        for link in category_links:
            print(link)
        


if __name__ == "__main__":
    start = time.time()
    itwork_scrapper = ItworkScrapper()
    asyncio.run(itwork_scrapper.main())
    end = time.time()
    print(f"Seconds {end - start}")

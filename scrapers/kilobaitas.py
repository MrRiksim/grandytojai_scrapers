import requests
import re
from bs4 import BeautifulSoup

from scrapers.dataclass.computer_part import ComputerPart
from scrapers.enums.computer_part_type import ComputerPartType
from scrapers.scrapper import Scrapper

class KilobaitasScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kilobaitas.lt"
        self.starting_url = "https://www.kilobaitas.lt/kompiuteriai_ir_komponentai/kompiuteriu_komponentai/kategorijos.aspx?groupfilterid=48"
        self.session = requests.Session()

    @staticmethod
    def getPageCategoriesAndUrls(soup: BeautifulSoup) -> list[str]:
        return [
            (
                f"{link.
                find('a').attrs.
                get('href')}&limit={
                    link.
                    find('span', class_='item-count').
                    get_text(strip=True).
                    removesuffix(')').
                    removeprefix('(')
                }", 
                link.find('a').attrs.get('title')
            ) 
                for link in soup.find_all('div', class_="category-title") 
                if link.find('a') 
        ]
    
    def getComputerPartData(self, category_item: BeautifulSoup, category: str) -> ComputerPart:
        item_title_el = category_item.find('a')
        part_name = item_title_el.attrs.get('title').strip()
        part_type = ComputerPartType.from_str(category).value[0]

        price = float(category_item.find('div', class_='item-price').find('span', string=re.compile('€')).get_text().strip().replace(',', '.').removesuffix("€"))
        part_url = f"{self.base_url}{item_title_el.attrs.get('href')}"
        image_url = f"{self.base_url}{category_item.find('img').attrs.get('src')}"

        barcode_parent_el = category_item.find('div', class_='extra-info')

        barcode = barcode_parent_el.find('span', class_='item-code').get_text().strip()
        
        return ComputerPart(
            barcode=barcode,
            part_name=part_name,
            part_type=part_type,
            price=price,
            image_url=image_url,
            store_url=part_url,
            store_name='Kilobaitas'
        )
    
    def sendScrappedComputerPart(self, computer_part: ComputerPart):
        try:
            response = self.api_client.post_data(self.computer_part_endpoint, computer_part.__dict__)
            if response.status_code == 201:
                self.created_count += 1
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                response = self.api_client.put_data(self.computer_part_endpoint, computer_part.__dict__)
                if response.status_code == 200:
                    self.updated_count += 1
            else:
                print(e)
        finally:
            self.total_scrapped_count += 1

    def main(self):
        session_content = self.session.get(self.starting_url, headers=self.headers)

        soup = BeautifulSoup(session_content.content, 'html.parser')
        category_links = self.getPageCategoriesAndUrls(soup)
        
        for category_tuple in category_links:
            category_url = category_tuple[0]
            session_content = self.session.get(f"{self.base_url}{category_url}")
            soup = BeautifulSoup(session_content.content, 'html.parser')

            if soup.find('div', class_='category-grid'):
                category_links.extend(self.getPageCategoriesAndUrls(soup))
                continue

            category_items = soup.find_all('div', class_='item-inner')
            for category_item in category_items:
                computer_part = self.getComputerPartData(category_item, category_tuple[1])

                self.sendScrappedComputerPart(computer_part)

            print(f"Category: {category_tuple[1]}")
            print(f"Newly created parts: {self.created_count}")
            print(f"Updated parts: {self.updated_count}")
            self.created_count = 0
            self.updated_count = 0
        print(f"Total scrapped parts: {self.total_scrapped_count}")

if __name__ == "__main__":
    kilobaitas_scrapper = KilobaitasScrapper()
    kilobaitas_scrapper.main()


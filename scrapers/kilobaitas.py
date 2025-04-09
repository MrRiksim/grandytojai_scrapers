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

class KilobaitasScrapper(Scrapper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://www.kilobaitas.lt"
        self.starting_url = "https://www.kilobaitas.lt/kompiuteriai_ir_komponentai/kompiuteriu_komponentai/kategorijos.aspx?groupfilterid=48"
        self.session = requests.Session()
        self.requests_results = None
        self.bad_barcodes_dict = None
        self.barcodes_got_out_of_name_list = []

    @staticmethod
    def getPageCategoriesAndUrls(soup: BeautifulSoup) -> list[str]:
        return [
            (
                f"{link.
                find('a').attrs.
                get('href')}&limit={
                    link.select_one('span.item-count').
                    get_text(strip=True).
                    removesuffix(')').
                    removeprefix('(')
                }", 
                link.find('a').attrs.get('title')
            ) 
                for link in soup.find_all('div', class_="category-title") 
                if link.find('a') 
        ]
    
    def getBarcodeOutOfName(self, barcode: str, part_name: str):
        barcode_no_suffix = barcode.removesuffix('...')

        barcode_with_white_space = barcode_no_suffix.split(' ')

        part_name = part_name.translate(str.maketrans({'/': ' ', ';': ' ', '|': ' '}))

        part_name_split = part_name.split(' ')
        for part_name_part in part_name_split:
            if len(barcode_with_white_space) > 1:
                if barcode_no_suffix in part_name_part:
                    self.barcodes_got_out_of_name_list.append({"original_barcode" : barcode_no_suffix, "out_of_name_barcode": part_name_part})
                    return part_name_part
            else:
                if barcode_with_white_space[-1] in part_name_part:
                    barcode_with_white_space[-1] = part_name_part
                    barcodes_with_white_space_to_return = ' '.join(barcode_with_white_space)
                    self.barcodes_got_out_of_name_list.append({"original_barcode" : barcode_no_suffix, "out_of_name_barcode": barcodes_with_white_space_to_return})
                    return barcodes_with_white_space_to_return

    
    def getComputerPartData(self, category_item: BeautifulSoup, category: str, ) -> ComputerPart:
        item_title_el = category_item.find('a')
        part_name = item_title_el.attrs.get('title').strip()
        part_type = ComputerPartType.from_str(category).value[0]

        price = float(category_item.find('span', class_='price').find(string=re.compile('€')).get_text().strip().replace(',', '.').removesuffix("€"))
        part_url = f"{self.base_url}{item_title_el.attrs.get('href')}"
        image_url = f"{self.base_url}{category_item.find('img').attrs.get('src')}"
        discount = category_item.find('span', class_='sale-item-label percent-discount').get_text()
        has_discount = int(discount.removesuffix('%')) > 20 if len(str(discount)) > 0 else False

        if (new_barcode_value := self.bad_barcode_results_dict.get(part_url.split('itemid=')[1].strip())) and (new_barcode_text := new_barcode_value.get('new_barcode')):
            barcode = new_barcode_text
        else:
            barcode = category_item.select_one('span.item-code').get_text().strip()
            if barcode.endswith('...'):
                barcode = self.getBarcodeOutOfName(barcode, part_name)
        
        return ComputerPart(
            barcode=barcode,
            part_name=part_name,
            part_type=part_type,
            price=price,
            image_url=image_url,
            store_url=part_url,
            store_name='Kilobaitas',
            has_discount=has_discount
        )
    
    async def sendScrappedComputerPart(self, async_session: aiohttp.ClientSession, computer_part: ComputerPart):
        try:
            response, status_code, url = await self.async_api_client._make_request(
                async_session=async_session,
                headers={"Content-Type": "application/json"},
                url=f"{BACKEND_BASE_URL_DEV}{self.computer_part_endpoint}", 
                method="POST", 
                data=computer_part.__dict__
            )
            if status_code == 201:
                self.created_count += 1
                self.total_scrapped_count += 1
        except aiohttp.ClientResponseError as e:
            if e.status == 409:
                response, status_code, url = await self.async_api_client._make_request(
                    async_session=async_session,
                    headers={"Content-Type": "application/json"},
                    url=f"{BACKEND_BASE_URL_DEV}{self.computer_part_endpoint}", 
                    method="PUT", 
                    data=computer_part.__dict__
                )
                if status_code == 200:
                    self.updated_count += 1
                    self.total_scrapped_count += 1
            else:
                print(e)


    async def main(self):
        session_content = self.session.get(self.starting_url, headers=self.headers)

        soup = BeautifulSoup(session_content.content, 'lxml')
        category_links = self.getPageCategoriesAndUrls(soup)

        session_results = await self.async_api_client._make_requests([f"{self.base_url}{category_tuple[0]}" for category_tuple in category_links], self.headers)

        for session_content, category_tuple in zip(session_results, category_links):
            soup = BeautifulSoup(session_content[0], 'lxml')

            if soup.find('div', class_='category-grid'):
                new_category_links = self.getPageCategoriesAndUrls(soup)
                category_links.extend(new_category_links)
                session_results.extend(await self.async_api_client._make_requests([f"{self.base_url}{category_tuple_new[0]}" for category_tuple_new in new_category_links], self.headers))
                continue

            category_items = soup.find_all('div', class_='item-inner')

            self.bad_barcode_results_dict = { category_item.find('a').attrs.get('href').split('itemid=')[1].strip() : { "url": f"{self.base_url}{category_item.find('a').attrs.get('href')}" } for category_item in category_items if category_item.find('span', 'item-code').get_text().strip().endswith('...')}

            bad_barcode_results = await self.async_api_client._make_requests([values['url'] for values in self.bad_barcode_results_dict.values() ], self.headers)

            for bad_barcode_session_content in bad_barcode_results:
                bad_barcode_soup_strained = SoupStrainer('span', class_='btn-blue')
                bad_barcode_soup = BeautifulSoup(bad_barcode_session_content[0], 'lxml', parse_only=bad_barcode_soup_strained)
                if barcode := bad_barcode_soup.select_one('#lytA_ctl08_lblCode'):
                    self.bad_barcode_results_dict[bad_barcode_session_content[2].split('itemid=')[1].strip()]['new_barcode'] = barcode.get_text()

            computer_parts_data = [self.getComputerPartData(category_item, category_tuple[1]) for category_item in category_items]
                
            async with aiohttp.ClientSession() as async_session:
                tasks = []
                for computer_part in computer_parts_data:
                    tasks.append(self.sendScrappedComputerPart(async_session, computer_part))
                await asyncio.gather(*tasks)


            print(f"Category: {category_tuple[1]}")
            print(f"Newly created parts: {self.created_count}")
            print(f"Updated parts: {self.updated_count}")
            self.created_count = 0
            self.updated_count = 0
        print(f"Total scrapped parts: {self.total_scrapped_count}")
        print(f"Fucked up barcodes, that were gotten out of the part name {len(self.barcodes_got_out_of_name_list)}")
        print(self.barcodes_got_out_of_name_list)

if __name__ == "__main__":
    start = time.time()
    kilobaitas_scrapper = KilobaitasScrapper()
    asyncio.run(kilobaitas_scrapper.main())
    end = time.time()
    print(f"Seconds {end - start}")


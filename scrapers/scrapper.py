from scrapers.api.api import ApiClient
from scrapers.api.async_api import AsyncAPIClient

class Scrapper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        self.api_client = ApiClient()
        self.async_api_client = AsyncAPIClient()
        self.computer_part_endpoint = "computerParts"
        self.created_count = 0
        self.updated_count = 0
        self.total_scrapped_count = 0

import json

from requests import post, put, HTTPError, Response
from urllib.parse import urljoin
from typing import Generic, TypeVar

from ..constants.url import BACKEND_BASE_URL_DEV

T = TypeVar('T')

class ApiClient:
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json"
        }

    def post_data(self, endpoint: str, payload: Generic[T]) -> Response:
        response = post(url=urljoin(BACKEND_BASE_URL_DEV, endpoint), data=json.dumps(payload), headers=self.headers)
        return response
        
    def put_data(self, endpoint: str, payload: Generic[T]) -> Response:
        response = put(url=urljoin(BACKEND_BASE_URL_DEV, endpoint), data=json.dumps(payload), headers=self.headers)
        return response
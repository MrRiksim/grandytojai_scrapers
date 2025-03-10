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
        try: 
            response = post(url=urljoin(BACKEND_BASE_URL_DEV, endpoint), data=json.dumps(payload), headers=self.headers)
            response.raise_for_status()
            return response
        except HTTPError as e:
            raise HTTPError(f"A HTTP error has occured when performing post request: {e}", response=e.response, request=e.request)
        except Exception as e:
            raise Exception(f"An unexpected exception occured: {e}")
        
    def put_data(self, endpoint: str, payload: Generic[T]) -> Response:
        try: 
            response = put(url=urljoin(BACKEND_BASE_URL_DEV, endpoint), data=json.dumps(payload), headers=self.headers)
            response.raise_for_status()
            return response
        except HTTPError as e:
            raise Exception(f"A HTTP error has occured when performing put request: {e}", response=e.response, request=e.request)
        except Exception as e:
            raise Exception(f"An unexpected exception occured: {e}")

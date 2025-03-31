from typing import Dict, Any

import aiohttp
import asyncio
import json

class AsyncAPIClient:
    def __init__(self):
        self.semaphore = asyncio.Semaphore(300)

    async def _make_request(self, async_session: aiohttp.ClientSession, url: str, headers: Dict[str, Any], method: str, data: Any): 
        async with self.semaphore:
            async with async_session.request(url=url, headers=headers, method=method, data=json.dumps(data)) as _response:
                response = await _response.text()
                return response, _response.status, url

            
    async def _make_requests(self, urls: list[str], headers: Dict[str, Any], method: str = "GET", data: Any = None):
        async with aiohttp.ClientSession() as async_session:
            tasks = []
            for url in urls:

                task = asyncio.create_task(
                    coro=self._make_request(
                        async_session=async_session,
                        url=url,
                        headers=headers,
                        method=method,
                        data=data
                    )
                )

                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=False)

            return responses
"""
HTTP session management with retry logic and rate limiting.
"""

import httpx
import asyncio
from typing import Optional
from loguru import logger

class HTTPSession:
    """
    Manages HTTP sessions with features like rate limiting, cookie handling,
    user-agent rotation, and retry logic with exponential backoff.
    """
    def __init__(self,
                 rate_limit: float = 0.5,  # seconds between requests
                 retries: int = 3,
                 backoff_factor: float = 0.5,
                 user_agents: Optional[list[str]] = None):
        self._client = httpx.AsyncClient()
        self._rate_limit = rate_limit
        self._retries = retries
        self._backoff_factor = backoff_factor
        self._last_request_time = 0.0
        self._user_agents = user_agents if user_agents else [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        ]
        self._user_agent_index = 0
        self._default_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def _wait_for_rate_limit(self):
        """Waits if necessary to respect the rate limit."""
        elapsed = asyncio.get_event_loop().time() - self._last_request_time
        if elapsed < self._rate_limit:
            await asyncio.sleep(self._rate_limit - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    def _get_next_user_agent(self) -> str:
        """Rotates user agents."""
        ua = self._user_agents[self._user_agent_index]
        self._user_agent_index = (self._user_agent_index + 1) % len(self._user_agents)
        return ua

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """
        Performs a GET request with retry logic and rate limiting.
        """
        headers = {**self._default_headers, **kwargs.pop('headers', {})}
        headers['User-Agent'] = self._get_next_user_agent()
        kwargs['headers'] = headers

        for attempt in range(self._retries):
            await self._wait_for_rate_limit()
            try:
                response = await self._client.get(url, **kwargs)
                response.raise_for_status()  # Raise an exception for bad status codes
                return response
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error on {url} (Attempt {attempt + 1}/{self._retries}): {e.response.status_code} - {e.response.text}")
                if attempt < self._retries - 1:
                    await asyncio.sleep(self._backoff_factor * (2 ** attempt))
                else:
                    raise
            except httpx.RequestError as e:
                logger.warning(f"Request error on {url} (Attempt {attempt + 1}/{self._retries}): {e}")
                if attempt < self._retries - 1:
                    await asyncio.sleep(self._backoff_factor * (2 ** attempt))
                else:
                    raise
        # If the loop finishes without returning, it means all retries failed.
        raise httpx.RequestError(f"Failed to get {url} after {self._retries} attempts.", request=httpx.Request(method="GET", url=url))


    async def post(self, url: str, data: Optional[dict] = None, json: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Performs a POST request with retry logic and rate limiting.
        """
        headers = {**self._default_headers, **kwargs.pop('headers', {})}
        headers['User-Agent'] = self._get_next_user_agent()
        kwargs['headers'] = headers

        for attempt in range(self._retries):
            await self._wait_for_rate_limit()
            try:
                response = await self._client.post(url, data=data, json=json, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error on {url} (Attempt {attempt + 1}/{self._retries}): {e.response.status_code} - {e.response.text}")
                if attempt < self._retries - 1:
                    await asyncio.sleep(self._backoff_factor * (2 ** attempt))
                else:
                    raise
            except httpx.RequestError as e:
                logger.warning(f"Request error on {url} (Attempt {attempt + 1}/{self._retries}): {e}")
                if attempt < self._retries - 1:
                    await asyncio.sleep(self._backoff_factor * (2 ** attempt))
                else:
                    raise
        # If the loop finishes without returning, it means all retries failed.
        raise httpx.RequestError(f"Failed to post to {url} after {self._retries} attempts.", request=httpx.Request(method="POST", url=url))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def close(self):
        """Closes the underlying HTTP client session."""
        await self._client.aclose()

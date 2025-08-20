import requests
from core.config import config

class HTTPClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(config.HEADERS)

    def get(self, url: str, stream: bool = False):
        try:
            response = self.session.get(url, stream=stream)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"HTTP GET Error for {url}: {e}")
            raise

    def post(self, url: str, data: dict):
        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"HTTP POST Error for {url}: {e}")
            raise

http_client = HTTPClient()

"""
HTML parsing utilities.
"""

from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin
from typing import Union

class HTMLParser:
    """
    Provides utilities for parsing HTML content.
    """

    def parse(self, html_content: str) -> BeautifulSoup:
        """
        Parses HTML content using BeautifulSoup.
        """
        return BeautifulSoup(html_content, 'html.parser')

    def extract_urls(self, element: Union[BeautifulSoup, Tag], base_url: str, selector: str, attribute: str = 'href') -> list[str]:
        """
        Extracts URLs from HTML based on a CSS selector and attribute.
        Normalizes URLs to be absolute.
        """
        urls = []
        for tag in element.select(selector):
            url_attr = tag.get(attribute)
            if isinstance(url_attr, str):
                urls.append(self.normalize_url(url_attr, base_url))
            elif isinstance(url_attr, list) and url_attr:
                # Handle cases where .get() might return a list (e.g., multiple attributes with same name)
                # For href/src, it's usually a single string, but being robust.
                for u in url_attr:
                    if isinstance(u, str):
                        urls.append(self.normalize_url(u, base_url))
        return urls

    def normalize_url(self, url: str, base_url: str) -> str:
        """
        Normalizes a URL to be absolute.
        """
        return urljoin(base_url, url)

    def extract_text(self, element: Union[BeautifulSoup, Tag], selector: str) -> str | None:
        """
        Extracts text content from an HTML element (BeautifulSoup object or Tag) based on a CSS selector.
        If the selector is empty, it extracts text directly from the provided element.
        """
        if not selector:
            return element.get_text(strip=True) if element else None
        selected_element = element.select_one(selector)
        return selected_element.get_text(strip=True) if selected_element else None

    def extract_attribute(self, element: Union[BeautifulSoup, Tag], selector: str, attribute: str) -> str | None:
        """
        Extracts an attribute's value from an HTML element (BeautifulSoup object or Tag) based on a CSS selector.
        """
        selected_element = element.select_one(selector)
        if selected_element:
            attr_value = selected_element.get(attribute)
            if isinstance(attr_value, str):
                return attr_value
            elif isinstance(attr_value, list) and attr_value:
                return attr_value[0] # Return the first one if it's a list
        return None

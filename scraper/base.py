"""
Base scraper interface.
"""

from abc import ABC, abstractmethod
from typing import List
from core.models import MangaMetadata, ChapterInfo, ImageInfo

class BaseScraper(ABC):
    """
    Abstract base class for all manga scrapers.
    Defines the interface that all site-specific scrapers must implement.
    """

    @abstractmethod
    async def search_manga(self, query: str) -> List[MangaMetadata]:
        """
        Searches for manga based on a query.
        """
        pass

    @abstractmethod
    async def get_chapter_urls(self, manga_url: str) -> List[ChapterInfo]:
        """
        Extracts chapter URLs for a given manga URL.
        """
        pass

    @abstractmethod
    async def get_image_urls(self, chapter_url: str) -> List[ImageInfo]:
        """
        Discovers image URLs within a chapter URL.
        """
        pass

    @abstractmethod
    async def parse_metadata(self, url: str) -> MangaMetadata:
        """
        Parses manga metadata from a given URL.
        """
        pass

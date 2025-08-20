"""
Base converter interface.
"""

from abc import ABC, abstractmethod
from typing import List
from core.models import ImageInfo

class BaseConverter(ABC):
    """
    Abstract base class for all manga converters.
    Defines the interface that all format-specific converters must implement.
    """

    @abstractmethod
    async def convert(self, images: List[ImageInfo], output_path: str, manga_title: str, chapter_title: str):
        """
        Converts a list of images into a specified format and saves it to output_path.
        """
        pass

"""
Individual download worker for images.
"""

import asyncio
from typing import List, Callable, Awaitable, Optional
from loguru import logger
import os
import cloudscraper # Import cloudscraper
import requests # Import requests for exception handling

from core.models import ImageInfo

class DownloadWorker:
    """
    Handles the download of individual images with retry logic and progress reporting.
    """
    def __init__(self,
                 output_dir: str,
                 max_workers: int = 8,
                 progress_callback: Optional[Callable[[int], Awaitable[None]]] = None):
        # Initialize cloudscraper for image downloads
        # Using a basic setup as per user's request for download functionality only
        # Initialize cloudscraper with optimal configuration for Cloudflare bypass
        # Initialize cloudscraper with a basic setup as per the working test.py script
        self._scraper = cloudscraper.create_scraper()
        self.output_dir = output_dir
        self.max_workers = max_workers
        self.progress_callback = progress_callback
        self._downloaded_count = 0
        os.makedirs(self.output_dir, exist_ok=True)

    async def download_images(self, images: List[ImageInfo], chapter_url: str):
        """
        Downloads a list of images concurrently.
        """
        self._downloaded_count = 0
        # Use a semaphore to limit concurrent downloads
        semaphore = asyncio.Semaphore(self.max_workers)
        tasks = []
        for image_info in images:
            tasks.append(self._download_single_image(image_info, chapter_url, semaphore))

        await asyncio.gather(*tasks)

    async def _download_single_image(self, image_info: ImageInfo, chapter_url: str, semaphore: asyncio.Semaphore):
        """
        Downloads a single image and saves it to the output directory.
        Uses asyncio.to_thread to run synchronous cloudscraper calls.
        """
        file_path = os.path.join(self.output_dir, image_info.filename)
        
        # Skip if file already exists
        if os.path.exists(file_path):
            logger.info(f"Skipping existing file: {image_info.filename}")
            self._downloaded_count += 1
            if self.progress_callback:
                await self.progress_callback(self._downloaded_count)
            return

        async with semaphore:
            try:
                logger.debug(f"Attempting to download image: {image_info.url} with Referer: {chapter_url}")
                # Use asyncio.to_thread to run the synchronous cloudscraper.get call
                headers = {
                    "Referer": chapter_url,  # Set Referer to the chapter page URL
                    "User-Agent": self._scraper.headers["User-Agent"],  # Use same UA cloudscraper uses
                }
                response = await asyncio.to_thread(self._scraper.get, image_info.url, headers=headers)
                logger.debug(f"Received response for {image_info.url}. Status: {response.status_code}")
                response.raise_for_status() # Raise an exception for bad status codes

                with open(file_path, "wb") as f:
                    f.write(response.content)
                image_info.file_path = file_path # Store the actual file path in ImageInfo
                logger.info(f"Successfully saved image: {image_info.filename} to {file_path}")
                self._downloaded_count += 1
                if self.progress_callback:
                    await self.progress_callback(self._downloaded_count)
            except requests.exceptions.RequestException as e: # Catch requests-specific exceptions from cloudscraper
                logger.error(f"Failed to download {image_info.filename} (Cloudscraper Request Error): {e}")
                image_info.file_path = None # Mark as failed or not available
            except Exception as e:
                logger.error(f"An unexpected error occurred while downloading {image_info.filename}: {e}")
                image_info.file_path = None # Mark as failed or not available

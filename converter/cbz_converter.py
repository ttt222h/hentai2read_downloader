"""
CBZ converter for manga images.
"""

import os
import zipfile
from typing import List
from loguru import logger
from core.models import ImageInfo
from converter.base import BaseConverter
from utils.file_utils import sanitize_filename # Import sanitize_filename

class CBZConverter(BaseConverter):
    """
    Converts a list of images into a CBZ archive.
    """

    async def convert(self, images: List[ImageInfo], output_path: str, manga_title: str, chapter_title: str):
        """
        Converts a list of images into a CBZ archive and saves it to output_path.

        Args:
            images (List[ImageInfo]): A list of ImageInfo objects representing the images to convert.
            output_path (str): The directory where the CBZ file will be saved.
            manga_title (str): The title of the manga.
            chapter_title (str): The title of the chapter.
        """
        if not images:
            raise ValueError("No images provided for CBZ conversion.")

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        sanitized_manga_title = sanitize_filename(manga_title)
        sanitized_chapter_title = sanitize_filename(chapter_title)
        cbz_filename = os.path.join(output_path, f"{sanitized_manga_title} - {sanitized_chapter_title}.cbz")

        with zipfile.ZipFile(cbz_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, image_info in enumerate(images):
                if not image_info.file_path:
                    logger.warning(f"Image file path is None for {image_info.filename}. Skipping.")
                    continue
                if not os.path.exists(image_info.file_path):
                    logger.warning(f"Image file not found at {image_info.file_path}. Skipping.")
                    continue
                try:
                    # Add image to the zip file with its original filename
                    zf.write(image_info.file_path, os.path.basename(image_info.file_path))
                except Exception as e:
                    logger.error(f"Error adding image {image_info.file_path} to CBZ: {e}")
                    continue

            # Optionally, add ComicInfo.xml for metadata (basic example)
            comic_info_content = f"""<?xml version="1.0"?>
<ComicInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <Title>{manga_title}</Title>
  <Series>{manga_title}</Series>
  <Number>{chapter_title}</Number>
  <Writer>Hentai2Read Downloader</Writer>
  <Summary>Downloaded from Hentai2Read</Summary>
</ComicInfo>"""
            zf.writestr("ComicInfo.xml", comic_info_content)

        logger.info(f"Successfully converted {len(images)} images to CBZ: {cbz_filename}")

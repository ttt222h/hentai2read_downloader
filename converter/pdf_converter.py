"""
PDF converter for manga images using ReportLab.
"""

import os
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image
from loguru import logger
from core.models import ImageInfo
from converter.base import BaseConverter
from utils.file_utils import sanitize_filename # Import sanitize_filename

class PDFConverter(BaseConverter):
    """
    Converts a list of images into a PDF file.
    """

    async def convert(self, images: List[ImageInfo], output_path: str, manga_title: str, chapter_title: str):
        """
        Converts a list of images into a PDF file and saves it to output_path.

        Args:
            images (List[ImageInfo]): A list of ImageInfo objects representing the images to convert.
            output_path (str): The directory where the PDF file will be saved.
            manga_title (str): The title of the manga.
            chapter_title (str): The title of the chapter.
        """
        if not images:
            raise ValueError("No images provided for PDF conversion.")

        # Ensure output directory exists
        os.makedirs(output_path, exist_ok=True)

        sanitized_manga_title = sanitize_filename(manga_title)
        sanitized_chapter_title = sanitize_filename(chapter_title)
        pdf_filename = os.path.join(output_path, f"{sanitized_manga_title} - {sanitized_chapter_title}.pdf")
        c = canvas.Canvas(pdf_filename, pagesize=letter)

        for i, image_info in enumerate(images):
            if not image_info.file_path:
                logger.warning(f"Image file path is None for {image_info.filename}. Skipping.")
                continue
            if not os.path.exists(image_info.file_path):
                logger.warning(f"Image file not found at {image_info.file_path}. Skipping.")
                continue
            try:
                img = Image.open(image_info.file_path)
                img_width, img_height = img.size

                # Calculate scaling to fit page
                page_width, page_height = letter
                scale_factor = min(page_width / img_width, page_height / img_height)

                scaled_width = img_width * scale_factor
                scaled_height = img_height * scale_factor

                # Center the image on the page
                x_offset = (page_width - scaled_width) / 2
                y_offset = (page_height - scaled_height) / 2

                c.drawImage(image_info.file_path, x_offset, y_offset, width=scaled_width, height=scaled_height)
                c.showPage() # Move to the next page for the next image
            except Exception as e:
                logger.error(f"Error processing image {image_info.file_path}: {e}")
                continue

        # Embed metadata (basic example)
        c.setAuthor("Hentai2Read Downloader")
        c.setTitle(f"{manga_title} - {chapter_title}")
        c.setSubject(f"Manga: {manga_title}, Chapter: {chapter_title}")

        c.save()
        logger.info(f"Successfully converted {len(images)} images to PDF: {pdf_filename}")

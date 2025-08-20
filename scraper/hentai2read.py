"""
Site-specific scraping logic for hentai2read.
"""

from scraper.base import BaseScraper
from scraper.parser import HTMLParser
from scraper.session import HTTPSession
import re
import httpx
import asyncio # Import asyncio for concurrent operations
from typing import List, Optional
from core.models import MangaMetadata, ChapterInfo, ImageInfo
from loguru import logger


class Hentai2ReadScraper(BaseScraper):
    """
    Implements scraping logic for hentai2read.com.
    """
    BASE_URL = "https://hentai2read.com"

    def __init__(self, session: HTTPSession):
        self.session = session
        self.parser = HTMLParser()

    async def search_manga(self, query: str) -> list[MangaMetadata]:
        """
        Searches for manga on hentai2read.
        """
        # Replace spaces with '+' for the search query in the URL
        formatted_query = query.replace(" ", "+")
        search_url = f"{self.BASE_URL}/hentai-list/search/{formatted_query}"
        response = await self.session.get(search_url)
        soup = self.parser.parse(response.text)

        manga_list = []
        # The user provided HTML structure for search results.
        # Each manga item is within a div with class "book-grid-item-container"
        for item in soup.select(".book-grid-item-container"):
            # Extract title from <a class="title"><span class="title-text">...</span></a>
            title_span = item.select_one("a.title span.title-text")
            title = self.parser.extract_text(title_span, "") if title_span else None

            # Extract URL from <a class="title" href="...">
            link_tag = item.select_one("a.title")
            href = link_tag.get("href") if link_tag else None
            url = self.parser.normalize_url(href, self.BASE_URL) if isinstance(href, str) else None

            # Extract cover URL from <picture> -> <img src="...">
            cover_img_tag = item.select_one("picture img")
            cover_src = cover_img_tag.get("src") if cover_img_tag else None
            cover_url = self.parser.normalize_url(cover_src, self.BASE_URL) if isinstance(cover_src, str) else None

            # Extract chapter count (pages) from the button with class 'si si-picture'
            chapter_count = 0
            pages_button = item.select_one("button.btn-custom2 i.si.si-picture")
            if pages_button and pages_button.parent:
                pages_text = pages_button.parent.get_text(strip=True)
                match = re.search(r'(\d[\d,]*)\s*pages', pages_text)
                if match:
                    try:
                        # Remove commas and convert to int
                        chapter_count = int(match.group(1).replace(',', ''))
                    except ValueError:
                        pass # Keep as 0 if conversion fails

            if title and url:
                # Create a dummy ChapterInfo list to hold the chapter_count for display
                # In a real scenario, this would be populated by get_chapter_urls
                dummy_chapters = [ChapterInfo(title="Dummy", url="", chapter_number=1) for _ in range(chapter_count)]

                manga_list.append(MangaMetadata(
                    title=title,
                    url=url,
                    cover_url=cover_url,
                    chapters=dummy_chapters # Populate with dummy chapters for count
                ))
        return manga_list

    async def get_chapter_urls(self, manga_url: str) -> list[ChapterInfo]:
        """
        Extracts chapter URLs for a given manga.
        """
        response = await self.session.get(manga_url)
        soup = self.parser.parse(response.text)

        chapter_list = []
        # Chapter links are within a div with class "media", and the actual link is an <a> tag with classes "pull-left font-w600"
        for item in soup.select("div.media a.pull-left.font-w600"):
            href = item.get("href")
            url = self.parser.normalize_url(href, self.BASE_URL) if isinstance(href, str) else None
            title = self.parser.extract_text(item, "") # Get text directly from the anchor tag

            if title and url:
                # Attempt to extract chapter number from title or URL
                chapter_number = None
                try:
                    # Simple regex to find numbers in "Chapter X" or "Ch. X"
                    match = re.search(r"(?:Chapter|Ch\.)\s*(\d+\.?\d*)", title, re.IGNORECASE)
                    if match:
                        chapter_number = float(match.group(1))
                    else:
                        # Fallback to extracting from URL if not found in title
                        url_match = re.search(r"chapter-(\d+\.?\d*)", url)
                        if url_match:
                            chapter_number = float(url_match.group(1))
                except ValueError:
                    pass # Ignore if conversion to float fails

                chapter_list.append(ChapterInfo(
                    title=title,
                    url=url,
                    chapter_number=chapter_number
                ))
        return chapter_list

    async def get_image_urls(self, chapter_url: str) -> list[ImageInfo]:
        """
        Discovers image URLs within a chapter by iterating through its pages until a 404.
        """
        image_urls = []
        page_number = 1
        previous_img_src = None
        CONCURRENT_PAGE_FETCHES = 5 # Number of pages to fetch concurrently

        while True:
            tasks = []
            current_batch_start_page = page_number
            
            # Create tasks for concurrent fetching
            for i in range(CONCURRENT_PAGE_FETCHES):
                page_url = f"{chapter_url}{current_batch_start_page + i}/"
                tasks.append(self.session.get(page_url))

            responses = await asyncio.gather(*tasks, return_exceptions=True) # Fetch concurrently

            found_new_image = False
            for i, response in enumerate(responses):
                current_page_num = current_batch_start_page + i
                page_url = f"{chapter_url}{current_page_num}/"

                if isinstance(response, httpx.Response):
                    if response.status_code == 200:
                        soup = self.parser.parse(response.text)
                        img_tag = soup.select_one("img#arf-reader")
                        if img_tag:
                            img_src = img_tag.get("src")
                            if isinstance(img_src, str):
                                normalized_img_src = self.parser.normalize_url(img_src, page_url)
                                
                                if previous_img_src and normalized_img_src == previous_img_src:
                                    return image_urls # Return immediately if repeated image found

                                image_urls.append(ImageInfo(
                                    url=normalized_img_src,
                                    filename=normalized_img_src.split('/')[-1],
                                    order=current_page_num - 1
                                ))
                                previous_img_src = normalized_img_src
                                found_new_image = True
                            else:
                                pass # Image src not found or invalid on page, continue
                        else:
                            pass # No img#arf-reader found on page, continue
                    elif response.status_code == 404:
                        return image_urls # Return immediately if 404 is encountered
                    else:
                        pass # HTTP error, continue to next response in batch
                elif isinstance(response, httpx.HTTPStatusError):
                    if response.response.status_code == 404:
                        return image_urls
                    else:
                        pass # HTTP error, continue
                elif isinstance(response, httpx.RequestError):
                    pass # Request error, continue
                else:
                    pass # Unexpected error, continue
            
            if not found_new_image:
                break # Break if no new images were found in the entire batch

            page_number += CONCURRENT_PAGE_FETCHES # Move to the next batch of pages
        
        return image_urls

    async def parse_metadata(self, url: str) -> MangaMetadata:
        """
        Parses manga metadata from a given URL.
        """
        response = await self.session.get(url)
        soup = self.parser.parse(response.text)

        # Attempt to extract title from the main manga page.
        # Based on the provided HTML snippet, the title might be within an <a> tag.
        # Let's try a more robust selector that looks for the main title on the page.
        # A common pattern is a large heading or a specific link.
        # Given the structure of the site, the title is often within a `div.title` or `h1` tag.
        # If `h1.title` doesn't work, let's try to find the `a` tag that contains the manga title.
        # The user provided: <a href="https://hentai2read.com/twin_sisters_blossom/">Twin Sisters Blossom <small class="text-danger">[Original]</small></a>
        # This suggests looking for an <a> tag that is likely the main title link.
        
        title = "Unknown Title" # Initialize with default

        # Attempt 1: Try h1.title
        title_element = soup.select_one("h1.title")
        if title_element:
            extracted_title = self.parser.extract_text(title_element, "")
            if extracted_title:
                title = extracted_title.strip()

        # Attempt 2: Fallback to <a> tag linking to the current URL
        if title == "Unknown Title":
            title_element = soup.select_one(f'a[href="{url}"]')
            if title_element:
                extracted_title = self.parser.extract_text(title_element, "")
                if extracted_title:
                    title = extracted_title.replace('[Original]', '').strip()

        # Attempt 3: Fallback to extracting from the URL itself
        if title == "Unknown Title":
            match = re.search(r'hentai2read\.com/([^/]+)/?$', url)
            if match:
                title = match.group(1).replace('_', ' ').title()
            # No else needed, as title remains "Unknown Title" if all attempts fail

        description = self.parser.extract_text(soup, ".description-container .description")
        cover_url = self.parser.extract_attribute(soup, ".cover-image img", "src")

        authors = []
        for author_tag in soup.select(".author-list a"): # Assuming authors are links in a list
            author_name = self.parser.extract_text(author_tag, "")
            if author_name:
                authors.append(author_name)

        tags = []
        for tag_tag in soup.select(".tag-list a"): # Assuming tags are links in a list
            tag_name = self.parser.extract_text(tag_tag, "")
            if tag_name:
                tags.append(tag_name)

        # Get chapters using the existing method
        chapters = await self.get_chapter_urls(url)

        return MangaMetadata(
            title=title if title else "Unknown Title",
            url=url,
            cover_url=self.parser.normalize_url(cover_url, url) if cover_url else None,
            description=description,
            authors=authors,
            tags=tags,
            chapters=chapters
        )

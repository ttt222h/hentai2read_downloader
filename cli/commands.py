import typer
from rich.console import Console
from cli.ui_components import display_welcome_message, create_manga_table, display_info, display_error, display_progress_status
from cli.prompts import ask_text_input, select_from_list, ask_confirmation, ask_integer_input, ask_delete_confirmation # Import new prompt
from core.models import MangaMetadata, DownloadTask, ProgressTracking, ChapterInfo, ImageInfo
from scraper.hentai2read import Hentai2ReadScraper
from scraper.session import HTTPSession
from downloader.manager import DownloadManager
from core.config import settings # Import the settings object
import asyncio
from typing import List, Optional
import os
from pathlib import Path # Import Path
from utils.file_utils import sanitize_filename # Import sanitize_filename

console = Console()

def register_commands(app: typer.Typer):
    @app.command(name="download", help="Start a new manga download.")
    def download_command():
        """
        Initiates an interactive manga download process.
        """
        display_welcome_message()
        console.print("\n[bold]Initiating download process...[/bold]")
        manga_url = ask_text_input("Enter Manga URL")
        if not manga_url:
            display_error("Manga URL cannot be empty.")
            return

        display_info(f"Attempting to download from: {manga_url}")
        
        async def _start_direct_download():
            session = HTTPSession()
            scraper = Hentai2ReadScraper(session)
            
            async def cli_progress_callback(progress: ProgressTracking):
                display_progress_status(progress)

            download_manager = DownloadManager(max_concurrent_downloads=4, progress_callback=cli_progress_callback)

            try:
                # First, parse metadata to get the manga title and chapters
                display_info(f"Fetching metadata for: {manga_url}")
                manga_metadata = await scraper.parse_metadata(manga_url)
                
                if not manga_metadata or not manga_metadata.chapters:
                    display_error(f"No chapters found for '{manga_url}'. Cannot proceed with download.")
                    return

                display_info(f"Found manga: [bold]{manga_metadata.title}[/bold] with {len(manga_metadata.chapters)} chapters.")
                
                for chapter in manga_metadata.chapters:
                    display_info(f"Fetching images for chapter: {chapter.title}")
                    images = await scraper.get_image_urls(chapter.url)
                    if not images:
                        display_error(f"No images found for chapter '{chapter.title}'. Skipping.")
                        continue

                    sanitized_manga_title = sanitize_filename(manga_metadata.title)
                    sanitized_chapter_title = sanitize_filename(chapter.title)
                    
                    download_task = DownloadTask(
                        manga_title=manga_metadata.title,
                        chapter_title=chapter.title,
                        chapter_url=chapter.url,
                        images=images,
                        output_dir=os.path.join("downloads", sanitized_manga_title, sanitized_chapter_title),
                        format="images"
                    )
                    await download_manager.add_download_task(download_task)
                    
                while download_manager.get_all_progress() and any(p.status in ["queued", "downloading", "converting"] for p in download_manager.get_all_progress()):
                    await asyncio.sleep(1)

                display_info(f"Download process for '{manga_metadata.title}' completed.")
                
                completed_tasks_data = download_manager._completed_tasks_data.values()

                if completed_tasks_data and ask_confirmation("Download complete. Do you want to convert the downloaded images to PDF or CBZ?"):
                    conversion_format = select_from_list("Select conversion format", ["pdf", "cbz"])
                    display_info(f"Starting conversion to {conversion_format.upper()} for downloaded chapters...")
                    
                    conversion_tasks = []
                    for task_to_convert in completed_tasks_data:
                        conversion_tasks.append(download_manager.convert_downloaded_chapter(task_to_convert, conversion_format))
                    
                    await asyncio.gather(*conversion_tasks)
                    display_info(f"Conversion process for '{manga_metadata.title}' completed.")

                    # Ask for image deletion after successful conversion
                    if ask_delete_confirmation("Conversion successful. Do you want to delete the original downloaded images?"):
                        display_info("Deleting original images...")
                        for task_to_clean in completed_tasks_data:
                            image_paths_to_cleanup = [img.file_path for img in task_to_clean.images if img.file_path]
                            from converter.image_processor import ImageProcessor # Import here to avoid circular dependency
                            ImageProcessor.cleanup_images(image_paths_to_cleanup)
                            display_info(f"Cleaned up images for chapter: {task_to_clean.chapter_title}")
                        display_info("Original images deleted.")

                elif completed_tasks_data:
                    display_info("Conversion skipped by user.")
                else:
                    display_info("No chapters were successfully downloaded for conversion.")

            except Exception as e:
                display_error(f"An error occurred during download: {e}")
            finally:
                await session.close()
                await download_manager.shutdown()

        asyncio.run(_start_direct_download())

    @app.command(name="search", help="Search for manga on hentai2read.")
    def search_command():
        """
        Interactively searches for manga and allows selection for download.
        """
        display_welcome_message()
        console.print("\n[bold]Initiating search process...[/bold]")
        query = ask_text_input("Enter search query")
        if not query:
            display_error("Search query cannot be empty.")
            return

        display_info(f"Searching for: '{query}'")

        async def _perform_search():
            session = HTTPSession()
            scraper = Hentai2ReadScraper(session)
            try:
                manga_results = await scraper.search_manga(query)
                return manga_results
            finally:
                await session.close()

        manga_results = asyncio.run(_perform_search())

        if not manga_results:
            display_info("No manga found for your query.")
            return

        console.print(create_manga_table(manga_results))

        selected_id_str = ask_text_input("Enter the ID of the manga to download (or press Enter to cancel)")
        if not selected_id_str:
            display_info("Manga selection cancelled.")
            return

        try:
            selected_id = int(selected_id_str)
            if 1 <= selected_id <= len(manga_results):
                selected_manga = manga_results[selected_id - 1]
                display_info(f"You selected: [bold]{selected_manga.title}[/bold]")
                confirm = ask_confirmation(f"Do you want to download '{selected_manga.title}'?")
                if confirm:
                    display_info(f"Starting download for '{selected_manga.title}'...")
                    
                    async def _start_download():
                        session = HTTPSession()
                        scraper = Hentai2ReadScraper(session)
                        
                        # Define a progress callback for CLI display
                        async def cli_progress_callback(progress: ProgressTracking):
                            display_progress_status(progress)

                        # Use a default value for max_concurrent_downloads, e.g., 4
                        download_manager = DownloadManager(max_concurrent_downloads=4, progress_callback=cli_progress_callback)

                        try:
                            # Get actual chapter URLs for the selected manga
                            chapters = await scraper.get_chapter_urls(selected_manga.url)
                            if not chapters:
                                display_error(f"No chapters found for '{selected_manga.title}'.")
                                return

                            # For simplicity, let's download all chapters found
                            # In a real app, you might prompt for chapter range
                            for chapter in chapters:
                                display_info(f"Fetching images for chapter: {chapter.title}")
                                images = await scraper.get_image_urls(chapter.url) # Call with only chapter.url
                                if not images:
                                    display_error(f"No images found for chapter '{chapter.title}'. Skipping.")
                                    continue

                                # Create a download task
                                sanitized_manga_title = sanitize_filename(selected_manga.title)
                                sanitized_chapter_title = sanitize_filename(chapter.title)

                                download_task = DownloadTask(
                                    manga_title=selected_manga.title,
                                    chapter_title=chapter.title,
                                    chapter_url=chapter.url,
                                    images=images,
                                    output_dir=os.path.join("downloads", sanitized_manga_title, sanitized_chapter_title),
                                    format="images" # Default to images for now, can be made configurable
                                )
                                await download_manager.add_download_task(download_task)
                                
                            # Keep the event loop running until all tasks are done
                            # This is a simplified approach for CLI. In a full app,
                            # the manager would run in the background.
                            while download_manager.get_all_progress() and any(p.status in ["queued", "downloading", "converting"] for p in download_manager.get_all_progress()):
                                await asyncio.sleep(1) # Wait for tasks to complete

                            display_info(f"Download process for '{selected_manga.title}' completed.")
                            
                            # Collect all successfully downloaded tasks for potential post-download conversion
                            # Access _completed_tasks_data directly from the manager
                            completed_tasks_data = download_manager._completed_tasks_data.values()

                            if completed_tasks_data and ask_confirmation("Download complete. Do you want to convert the downloaded images to PDF or CBZ?"):
                                conversion_format = select_from_list("Select conversion format", ["pdf", "cbz"])
                                display_info(f"Starting conversion to {conversion_format.upper()} for downloaded chapters...")
                                
                                conversion_tasks = []
                                for task_to_convert in completed_tasks_data:
                                    conversion_tasks.append(download_manager.convert_downloaded_chapter(task_to_convert, conversion_format))
                                
                                await asyncio.gather(*conversion_tasks)
                                display_info(f"Conversion process for '{selected_manga.title}' completed.")

                                # Ask for image deletion after successful conversion
                                if ask_delete_confirmation("Conversion successful. Do you want to delete the original downloaded images?"):
                                    display_info("Deleting original images...")
                                    for task_to_clean in completed_tasks_data:
                                        image_paths_to_cleanup = [img.file_path for img in task_to_clean.images if img.file_path]
                                        from converter.image_processor import ImageProcessor # Import here to avoid circular dependency
                                        ImageProcessor.cleanup_images(image_paths_to_cleanup)
                                        display_info(f"Cleaned up images for chapter: {task_to_clean.chapter_title}")
                                    display_info("Original images deleted.")

                            elif completed_tasks_data:
                                display_info("Conversion skipped by user.")
                            else:
                                display_info("No chapters were successfully downloaded for conversion.")

                        except Exception as e:
                            display_error(f"An error occurred during download: {e}")
                        finally:
                            await session.close()
                            await download_manager.shutdown() # Ensure manager resources are released

                    asyncio.run(_start_download())
                else:
                    display_info("Download cancelled by user.")
            else:
                display_error("Invalid manga ID.")
        except ValueError:
            display_error("Invalid input. Please enter a number.")

    @app.command(name="config", help="Manage application configuration.")
    def config_command():
        """
        Interactively manages application configuration.
        """
        display_welcome_message()
        console.print("\n[bold]Managing configuration...[/bold]")

        download_path = ask_text_input("Enter default download path", default="./downloads")
        max_downloads = ask_integer_input("Enter max concurrent downloads", default=4)
        
        # Update settings object
        settings.DOWNLOAD_DIR = Path(download_path).resolve()
        settings.MAX_CONCURRENT_DOWNLOADS = max_downloads
        
        display_info(f"New download path: {settings.DOWNLOAD_DIR}")
        display_info(f"New max concurrent downloads: {settings.MAX_CONCURRENT_DOWNLOADS}")
        
        confirm_save = ask_confirmation("Save these settings?")
        if confirm_save:
            try:
                settings.save_to_env()
                console.print("[bold green]Settings saved successfully to .env file.[/bold green]")
            except Exception as e:
                display_error(f"Failed to save settings: {e}")
        else:
            display_info("Settings not saved.")

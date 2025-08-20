"""
Download Worker Thread

Background thread for handling download operations in the GUI.
"""

import asyncio
import os
from typing import Dict, Any, Optional
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path

from loguru import logger
from core.models import DownloadTask, ProgressTracking
from core.config import settings
from scraper.hentai2read import Hentai2ReadScraper
from scraper.session import HTTPSession
from downloader.manager import DownloadManager
from utils.file_utils import sanitize_filename


class DownloadWorkerThread(QThread):
    """
    Background thread for download operations.
    
    Handles async download operations without blocking the GUI.
    """
    
    # Signals
    progress_updated = pyqtSignal(str, object)  # task_id, ProgressTracking object
    download_completed = pyqtSignal(str)        # task_id
    error_occurred = pyqtSignal(str, str)       # task_id, error_message
    metadata_fetched = pyqtSignal(str, object)  # url, MangaMetadata
    
    def __init__(self):
        """Initialize the download worker thread."""
        super().__init__()
        
        self.download_manager: Optional[DownloadManager] = None
        self.session: Optional[HTTPSession] = None
        self.scraper: Optional[Hentai2ReadScraper] = None
        self.pending_tasks = []
        self.running = False
        self.task_counter = 0
    
    def add_download_task(self, url: str, options: Dict[str, Any]) -> str:
        """
        Add a download task to the queue.
        
        Args:
            url: Manga URL to download
            options: Download options (format, concurrent, etc.)
            
        Returns:
            Task ID for tracking
        """
        task_id = f"task_{self.task_counter}"
        self.task_counter += 1
        
        self.pending_tasks.append((task_id, url, options))
        
        if not self.running:
            self.start()
        
        return task_id
    
    def run(self):
        """Main thread execution."""
        self.running = True
        try:
            asyncio.run(self._async_run())
        except Exception as e:
            logger.error(f"Download thread error: {e}")
        finally:
            self.running = False
    
    async def _async_run(self):
        """Async execution of download tasks."""
        self.session = HTTPSession()
        self.scraper = Hentai2ReadScraper(self.session)
        self.download_manager = DownloadManager(
            max_concurrent_downloads=settings.MAX_CONCURRENT_DOWNLOADS,
            progress_callback=self._progress_callback
        )
        
        try:
            while self.pending_tasks:
                task_id, url, options = self.pending_tasks.pop(0)
                await self._process_download(task_id, url, options)
        except Exception as e:
            logger.error(f"Download processing error: {e}")
        finally:
            await self._cleanup()
    
    async def _process_download(self, task_id: str, url: str, options: Dict[str, Any]):
        """
        Process a single download task.
        
        Args:
            task_id: Unique task identifier
            url: Manga URL
            options: Download options
        """
        try:
            logger.info(f"Processing download task {task_id}: {url}")
            
            # Check if scraper and download manager are initialized
            if not self.scraper or not self.download_manager:
                self.error_occurred.emit(task_id, "Download components not initialized")
                return
            
            # Fetch metadata
            manga_metadata = await self.scraper.parse_metadata(url)
            if not manga_metadata or not manga_metadata.chapters:
                self.error_occurred.emit(task_id, "No chapters found for this manga")
                return
            
            # Emit metadata for UI updates
            self.metadata_fetched.emit(url, manga_metadata)
            
            # Process each chapter
            for chapter in manga_metadata.chapters:
                chapter_task_id = f"{task_id}_chapter_{chapter.chapter_number or 0}"
                
                # Get images for chapter
                images = await self.scraper.get_image_urls(chapter.url)
                if not images:
                    logger.warning(f"No images found for chapter: {chapter.title}")
                    continue
                
                # Create download task
                sanitized_manga_title = sanitize_filename(manga_metadata.title)
                sanitized_chapter_title = sanitize_filename(chapter.title)
                
                download_task = DownloadTask(
                    manga_title=manga_metadata.title,
                    chapter_title=chapter.title,
                    chapter_url=chapter.url,
                    images=images,
                    output_dir=os.path.join(
                        "downloads",
                        sanitized_manga_title,
                        sanitized_chapter_title
                    ),
                    format=options.get('format', 'images')
                )
                
                # Add to download manager with the original task_id for tracking
                await self.download_manager.add_download_task(download_task, task_id)
            
            # Wait for all downloads to complete
            while self.download_manager.get_all_progress():
                active_progress = [
                    p for p in self.download_manager.get_all_progress()
                    if p.status in ["queued", "downloading", "converting"]
                ]
                if not active_progress:
                    break
                await asyncio.sleep(1)
            
            # Handle post-download conversion if needed
            if options.get('auto_convert') and options.get('format') != 'images':
                await self._handle_conversion(task_id, options)
            
            self.download_completed.emit(task_id)
            logger.info(f"Download task {task_id} completed successfully")
            
        except Exception as e:
            error_msg = f"Download failed: {str(e)}"
            logger.error(f"Task {task_id} error: {error_msg}")
            self.error_occurred.emit(task_id, error_msg)
    
    async def _handle_conversion(self, task_id: str, options: Dict[str, Any]):
        """
        Handle post-download conversion.
        
        Args:
            task_id: Task identifier
            options: Download options including format
        """
        try:
            format_type = options.get('format', 'images')
            if format_type == 'images' or not self.download_manager:
                return
            
            logger.info(f"Starting conversion to {format_type} for task {task_id}")
            
            # Get completed tasks from download manager
            completed_tasks = list(self.download_manager._completed_tasks_data.values())
            
            # Convert each completed task
            for task in completed_tasks:
                await self.download_manager.convert_downloaded_chapter(task, format_type)
            
            logger.info(f"Conversion completed for task {task_id}")
            
        except Exception as e:
            logger.error(f"Conversion error for task {task_id}: {e}")
            self.error_occurred.emit(task_id, f"Conversion failed: {str(e)}")
    
    async def _progress_callback(self, progress: ProgressTracking):
        """
        Handle progress updates from download manager.
        
        Args:
            progress: Progress tracking object
        """
        # Use the original task ID if available, otherwise create one from the chapter title
        if progress.original_task_id:
            task_id = progress.original_task_id
        else:
            # Fallback to creating a task ID from the progress info
            task_id = f"{progress.current_chapter or 'unknown'}"
        self.progress_updated.emit(task_id, progress)
    
    async def _cleanup(self):
        """Clean up resources."""
        try:
            if self.session:
                await self.session.close()
            if self.download_manager:
                await self.download_manager.shutdown()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
    
    def stop_downloads(self):
        """Stop all downloads and clean up."""
        self.pending_tasks.clear()
        if self.isRunning():
            self.terminate()
            self.wait()
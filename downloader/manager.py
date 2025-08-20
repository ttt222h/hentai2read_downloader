"""
Download orchestration and management.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Awaitable, Optional
from loguru import logger
from pathlib import Path # Import Path

from core.models import DownloadTask, ProgressTracking, ImageInfo
from downloader.worker import DownloadWorker
from downloader.queue import DownloadQueue
from scraper.session import HTTPSession
from converter.pdf_converter import PDFConverter
from converter.cbz_converter import CBZConverter
from converter.image_processor import ImageProcessor
from core.config import settings # Import settings

class DownloadManager:
    """
    Coordinates multi-threaded downloads, manages the download queue,
    aggregates progress, and handles errors with retry logic.
    """
    def __init__(self,
                 max_concurrent_downloads: int = 4,
                 max_workers_per_download: int = 8,
                 progress_callback: Optional[Callable[[ProgressTracking], Awaitable[None]]] = None):
        self.max_concurrent_downloads = max_concurrent_downloads
        self.max_workers_per_download = max_workers_per_download
        self.progress_callback = progress_callback
        self.download_queue = DownloadQueue()
        self._executor = ThreadPoolExecutor(max_concurrent_downloads)
        self._active_downloads = {} # {task_id: asyncio.Task}
        self._progress_trackers = {} # {task_id: ProgressTracking}
        self._completed_tasks_data = {} # {task_id: DownloadTask} to store completed tasks for post-processing

    async def add_download_task(self, task: DownloadTask, original_task_id: Optional[str] = None):
        """
        Adds a new download task to the queue.
        
        Args:
            task: The download task to add
            original_task_id: The original task ID from the download worker thread for tracking
        """
        task_id = f"{task.manga_title}-{task.chapter_title}"
        if task_id in self._active_downloads:
            logger.warning(f"Task {task_id} already in progress or queued.")
            return

        await self.download_queue.add_task(task) # Await add_task
        self._progress_trackers[task_id] = ProgressTracking(
            total_images=len(task.images),
            current_chapter=task.chapter_title,
            status="queued",
            original_task_id=original_task_id
        )
        await self._report_progress(task_id)
        logger.info(f"Added download task: {task_id}")
        asyncio.create_task(self._process_queue()) # Start processing queue in background

    async def _process_queue(self):
        """
        Continuously processes the download queue.
        """
        while True:
            if len(self._active_downloads) < self.max_concurrent_downloads:
                task = await self.download_queue.get_next_task() # Await get_next_task
                if task:
                    task_id = f"{task.manga_title}-{task.chapter_title}"
                    logger.info(f"Starting download for task: {task_id}")
                    self._progress_trackers[task_id].status = "downloading"
                    asyncio.create_task(self._execute_download(task, task_id))
                else:
                    await asyncio.sleep(1) # Wait a bit if queue is empty
            else:
                await asyncio.sleep(1) # Wait if max concurrent downloads reached

    async def _execute_download(self, task: DownloadTask, task_id: str):
        """
        Executes a single download task.
        """
        self._active_downloads[task_id] = asyncio.current_task()
        
        # Ensure the base download directory exists
        settings.DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

        # Construct the full output path using Path objects for robustness
        # The task.output_dir already contains sanitized manga/chapter titles
        full_output_dir = settings.DOWNLOAD_DIR / Path(task.output_dir).relative_to("downloads")

        worker = DownloadWorker(
            output_dir=str(full_output_dir), # Convert back to string for os.makedirs in worker
            max_workers=self.max_workers_per_download,
            progress_callback=lambda downloaded: self._update_image_progress(task_id, downloaded)
        )
        try:
            await worker.download_images(task.images, task.chapter_url)
            logger.info(f"Download completed for {task_id}. Starting conversion...")
            self._progress_trackers[task_id].status = "converting"
            await self._report_progress(task_id)

            if task.format == "pdf":
                converter = PDFConverter()
            elif task.format == "cbz":
                converter = CBZConverter()
            else:
                converter = None # No conversion needed if format is "images"

            if converter:
                # Pass the full_output_dir to the converter
                await converter.convert(task.images, str(full_output_dir), task.manga_title, task.chapter_title)
                logger.info(f"Conversion to {task.format.upper()} completed for {task_id}.")
                
                # Cleanup original images if they are not the final desired format
                if task.format != "images" and settings.DELETE_IMAGES_AFTER_CONVERSION:
                    image_paths_to_cleanup = [img.file_path for img in task.images if img.file_path]
                    ImageProcessor.cleanup_images(image_paths_to_cleanup)
                    logger.info(f"Cleaned up original image files for {task_id}.")

            self._progress_trackers[task_id].status = "completed"
            logger.info(f"Task {task_id} fully processed.")

        except Exception as e:
            self._progress_trackers[task_id].status = "failed"
            self._progress_trackers[task_id].errors.append(str(e))
            logger.error(f"Task failed for {task_id}: {e}")
        finally:
            if self._progress_trackers[task_id].status == "completed":
                self._completed_tasks_data[task_id] = task # Store the task if completed successfully
            del self._active_downloads[task_id]
            await self._report_progress(task_id)
            # The _process_queue loop will pick up the next task

    async def convert_downloaded_chapter(self, task: DownloadTask, target_format: str):
        """
        Converts a previously downloaded chapter to the specified format.
        This is called after the initial image download is complete.
        """
        task_id = f"{task.manga_title}-{task.chapter_title}"
        logger.info(f"Starting post-download conversion for {task_id} to {target_format.upper()}...")
        
        if task_id not in self._progress_trackers:
            self._progress_trackers[task_id] = ProgressTracking(
                total_images=len(task.images),
                current_chapter=task.chapter_title,
                status="converting"
            )
        else:
            self._progress_trackers[task_id].status = "converting"
        await self._report_progress(task_id)

        try:
            if target_format == "pdf":
                converter = PDFConverter()
            elif target_format == "cbz":
                converter = CBZConverter()
            else:
                logger.warning(f"Unsupported conversion format: {target_format}. Skipping conversion for {task_id}.")
                self._progress_trackers[task_id].status = "completed"
                await self._report_progress(task_id)
                return

            # Construct the full output path using Path objects for robustness
            full_output_dir = settings.DOWNLOAD_DIR / Path(task.output_dir).relative_to("downloads")
            await converter.convert(task.images, str(full_output_dir), task.manga_title, task.chapter_title)
            logger.info(f"Post-download conversion to {target_format.upper()} completed for {task_id}.")
            
            # Cleanup original images if they are not the final desired format and setting is enabled
            if target_format != "images" and settings.DELETE_IMAGES_AFTER_CONVERSION:
                image_paths_to_cleanup = [img.file_path for img in task.images if img.file_path]
                ImageProcessor.cleanup_images(image_paths_to_cleanup)
                logger.info(f"Cleaned up original image files for {task_id}.")
            
            self._progress_trackers[task_id].status = "completed"
            logger.info(f"Task {task_id} fully processed (including post-download conversion).")

        except Exception as e:
            self._progress_trackers[task_id].status = "failed"
            self._progress_trackers[task_id].errors.append(f"Conversion error: {e}")
            logger.error(f"Post-download conversion failed for {task_id}: {e}")
        finally:
            await self._report_progress(task_id)

    async def _update_image_progress(self, task_id: str, downloaded_count: int):
        """
        Updates the progress for a specific task and reports it.
        """
        if task_id in self._progress_trackers:
            self._progress_trackers[task_id].downloaded_images = downloaded_count
            await self._report_progress(task_id)

    async def _report_progress(self, task_id: str):
        """
        Reports the current progress of a task via the callback.
        """
        if self.progress_callback and task_id in self._progress_trackers:
            await self.progress_callback(self._progress_trackers[task_id])

    def get_all_progress(self) -> List[ProgressTracking]:
        """
        Returns the current progress of all active and queued downloads.
        """
        return list(self._progress_trackers.values())

    async def shutdown(self):
        """
        Shuts down the download manager and its resources.
        """
        self._executor.shutdown(wait=True)
        self._completed_tasks_data.clear() # Clear completed tasks on shutdown
        logger.info("DownloadManager shut down.")

"""
Progress tracking for downloads.
"""

import asyncio
from typing import Dict, Any, Callable, Awaitable, Optional
from core.models import ProgressTracking
from loguru import logger

class ProgressTracker:
    """
    Manages and aggregates progress for multiple download tasks.
    Can report overall progress via a callback.
    """
    def __init__(self, overall_progress_callback: Optional[Callable[[Dict[str, ProgressTracking]], Awaitable[None]]] = None):
        self._tasks_progress: Dict[str, ProgressTracking] = {}
        self._overall_progress_callback = overall_progress_callback
        self._lock = asyncio.Lock() # For thread-safe access

    async def update_progress(self, task_id: str, progress: ProgressTracking):
        """
        Updates the progress for a specific task.
        """
        async with self._lock:
            self._tasks_progress[task_id] = progress
            logger.debug(f"Progress update for {task_id}: {progress.downloaded_images}/{progress.total_images} ({progress.status})")
            if self._overall_progress_callback:
                await self._overall_progress_callback(self._tasks_progress)

    async def get_all_progress(self) -> Dict[str, ProgressTracking]:
        """
        Returns the current progress of all tracked tasks.
        """
        async with self._lock:
            return self._tasks_progress.copy()

    async def get_task_progress(self, task_id: str) -> Optional[ProgressTracking]:
        """
        Returns the progress for a specific task.
        """
        async with self._lock:
            return self._tasks_progress.get(task_id)

    async def remove_task_progress(self, task_id: str):
        """
        Removes a task's progress from tracking.
        """
        async with self._lock:
            if task_id in self._tasks_progress:
                del self._tasks_progress[task_id]
                logger.info(f"Removed progress for task: {task_id}")
                if self._overall_progress_callback:
                    await self._overall_progress_callback(self._tasks_progress)

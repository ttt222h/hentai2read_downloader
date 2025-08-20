"""
Download queue management.
"""

import asyncio
from collections import deque
from typing import Optional
from core.models import DownloadTask

class DownloadQueue:
    """
    Manages a queue of download tasks.
    Currently a simple FIFO queue, can be extended for priority queuing.
    """
    def __init__(self):
        self._queue: deque[DownloadTask] = deque()
        self._lock = asyncio.Lock() # For thread-safe access if needed in multi-threaded context

    async def add_task(self, task: DownloadTask):
        """
        Adds a download task to the queue.
        """
        async with self._lock:
            self._queue.append(task)

    async def get_next_task(self) -> Optional[DownloadTask]:
        """
        Retrieves the next task from the queue.
        """
        async with self._lock:
            if self._queue:
                return self._queue.popleft()
            return None

    async def is_empty(self) -> bool:
        """
        Checks if the queue is empty.
        """
        async with self._lock:
            return not bool(self._queue)

    async def size(self) -> int:
        """
        Returns the current size of the queue.
        """
        async with self._lock:
            return len(self._queue)

"""
Pydantic models for data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class MangaMetadata(BaseModel):
    """
    Represents metadata for a manga series.
    """
    title: str
    url: str
    cover_url: Optional[str] = None
    description: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    chapters: List['ChapterInfo'] = Field(default_factory=list)

class ChapterInfo(BaseModel):
    """
    Represents information for a single chapter.
    """
    title: str
    url: str
    chapter_number: Optional[float] = None
    pages: List['ImageInfo'] = Field(default_factory=list)

class ImageInfo(BaseModel):
    """
    Represents information for a single image within a chapter.
    """
    url: str
    filename: str
    order: int
    file_path: Optional[str] = None # Local path where the image is saved

class DownloadTask(BaseModel):
    """
    Represents a single download task.
    """
    manga_title: str
    chapter_title: str
    chapter_url: str
    images: List[ImageInfo]
    output_dir: str
    format: str # e.g., "pdf", "cbz", "images"

class ProgressTracking(BaseModel):
    """
    Represents the progress of a download.
    """
    total_images: int = 0
    downloaded_images: int = 0
    current_chapter: Optional[str] = None
    status: str = "pending" # e.g., "pending", "downloading", "converting", "completed", "failed"
    errors: List[str] = Field(default_factory=list)
    original_task_id: Optional[str] = None # Original task ID from the download worker thread

# Update forward references
MangaMetadata.model_rebuild()
ChapterInfo.model_rebuild()

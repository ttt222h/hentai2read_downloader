"""
Drag & Drop Handler

Handles drag and drop functionality for URLs and files.
"""

from typing import List, Callable, Optional
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QWidget

from loguru import logger
import re


class DragDropHandler(QObject):
    """
    Handler for drag and drop operations.
    
    Supports dropping URLs and text files containing URLs.
    """
    
    # Signals
    urls_dropped = pyqtSignal(list)  # List of URLs
    
    def __init__(self, target_widget: QWidget, parent: Optional[QObject] = None):
        """
        Initialize the drag drop handler.
        
        Args:
            target_widget: Widget to enable drag/drop on
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.target_widget = target_widget
        self.url_pattern = re.compile(
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        )
        
        # Enable drag and drop on target widget
        self._setup_drag_drop()
        
        logger.debug(f"Drag drop handler initialized for {target_widget.__class__.__name__}")
    
    def _setup_drag_drop(self) -> None:
        """Setup drag and drop on the target widget."""
        self.target_widget.setAcceptDrops(True)
        
        # Override drag/drop methods
        self.target_widget.dragEnterEvent = self._drag_enter_event
        self.target_widget.dragMoveEvent = self._drag_move_event
        self.target_widget.dropEvent = self._drop_event
    
    def _drag_enter_event(self, event: QDragEnterEvent) -> None:
        """
        Handle drag enter event.
        
        Args:
            event: Drag enter event
        """
        mime_data = event.mimeData()
        
        # Check if we have URLs or text
        if mime_data.hasUrls() or mime_data.hasText():
            # Check if any URLs are valid hentai2read URLs
            urls = self._extract_urls_from_mime_data(mime_data)
            valid_urls = self._filter_valid_urls(urls)
            
            if valid_urls:
                event.acceptProposedAction()
                logger.debug(f"Drag enter accepted: {len(valid_urls)} valid URLs")
            else:
                event.ignore()
                logger.debug("Drag enter ignored: no valid URLs")
        else:
            event.ignore()
            logger.debug("Drag enter ignored: no URLs or text")
    
    def _drag_move_event(self, event) -> None:
        """
        Handle drag move event.
        
        Args:
            event: Drag move event
        """
        # Accept the drag move if we accepted the drag enter
        if event.proposedAction() == Qt.DropAction.CopyAction:
            event.acceptProposedAction()
    
    def _drop_event(self, event: QDropEvent) -> None:
        """
        Handle drop event.
        
        Args:
            event: Drop event
        """
        mime_data = event.mimeData()
        
        try:
            # Extract URLs from dropped data
            urls = self._extract_urls_from_mime_data(mime_data)
            valid_urls = self._filter_valid_urls(urls)
            
            if valid_urls:
                # Emit signal with valid URLs
                self.urls_dropped.emit(valid_urls)
                event.acceptProposedAction()
                logger.info(f"Dropped {len(valid_urls)} valid URLs")
            else:
                event.ignore()
                logger.warning("Drop ignored: no valid URLs found")
                
        except Exception as e:
            logger.error(f"Error handling drop event: {e}")
            event.ignore()
    
    def _extract_urls_from_mime_data(self, mime_data) -> List[str]:
        """
        Extract URLs from MIME data.
        
        Args:
            mime_data: QMimeData object
            
        Returns:
            List of extracted URLs
        """
        urls = []
        
        # Check for URL list
        if mime_data.hasUrls():
            for url in mime_data.urls():
                url_string = url.toString()
                if url_string:
                    urls.append(url_string)
        
        # Check for text content
        if mime_data.hasText():
            text = mime_data.text()
            # Find URLs in text using regex
            found_urls = self.url_pattern.findall(text)
            urls.extend(found_urls)
            
            # Also check if the entire text is a URL
            if text.strip().startswith(('http://', 'https://')):
                urls.append(text.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def _filter_valid_urls(self, urls: List[str]) -> List[str]:
        """
        Filter URLs to only include valid hentai2read URLs.
        
        Args:
            urls: List of URLs to filter
            
        Returns:
            List of valid hentai2read URLs
        """
        valid_urls = []
        
        for url in urls:
            if self._is_valid_hentai2read_url(url):
                valid_urls.append(url)
        
        return valid_urls
    
    def _is_valid_hentai2read_url(self, url: str) -> bool:
        """
        Check if URL is a valid hentai2read URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if valid hentai2read URL
        """
        try:
            # Basic validation
            if not url.startswith('https://hentai2read.com/'):
                return False
            
            # Check for manga URL pattern
            # Valid patterns: /manga/title/ or /manga/title/chapter/
            if '/manga/' in url:
                return True
            
            return False
            
        except Exception as e:
            logger.debug(f"URL validation error for {url}: {e}")
            return False
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable drag and drop.
        
        Args:
            enabled: Whether to enable drag and drop
        """
        self.target_widget.setAcceptDrops(enabled)
        logger.debug(f"Drag drop {'enabled' if enabled else 'disabled'}")
    
    def add_url_validator(self, validator: Callable[[str], bool]) -> None:
        """
        Add a custom URL validator.
        
        Args:
            validator: Function that takes a URL and returns bool
        """
        # Store the original validator
        original_validator = self._is_valid_hentai2read_url
        
        # Create new validator that uses both
        def combined_validator(url: str) -> bool:
            return original_validator(url) and validator(url)
        
        # Replace the validator
        self._is_valid_hentai2read_url = combined_validator
        
        logger.debug("Custom URL validator added")
"""
Download Management Widget

This module provides the main download management interface
with URL input, queue display, and progress tracking.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QListWidget, 
    QListWidgetItem, QComboBox, QCheckBox, QSpinBox,
    QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from loguru import logger
from core.models import ProgressTracking, MangaMetadata
from gui.components import DownloadWorkerThread, QueueItemWidget, DragDropHandler


class DownloadWidget(QWidget):
    """
    Download management widget with modern interface.
    
    Provides URL input, download queue display, progress tracking,
    and download control functionality.
    """
    
    # Signals
    download_requested = pyqtSignal(str, dict)  # URL, options
    download_stats_changed = pyqtSignal(dict)  # Statistics
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the download widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Initialize state
        self.queue_items = {}  # task_id -> QueueItemWidget
        self.download_thread = DownloadWorkerThread()
        self.stats_timer = QTimer()
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._setup_signals()
        self._setup_timer()
        self._setup_drag_drop()
        
        logger.info("Download widget initialized")
    
    def _setup_ui(self) -> None:
        """Setup the complete download widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("📥 Download Management")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # URL Input Section
        input_section = self._create_input_section()
        splitter.addWidget(input_section)
        
        # Download Queue Section
        queue_section = self._create_queue_section()
        splitter.addWidget(queue_section)
        
        # Set splitter proportions
        splitter.setSizes([200, 400])
        layout.addWidget(splitter)
    
    def _create_input_section(self) -> QWidget:
        """Create the URL input and options section."""
        section = QFrame()
        section.setObjectName("GlassCard")
        section.setMaximumHeight(180)
        
        layout = QVBoxLayout(section)
        
        # URL Input
        url_layout = QHBoxLayout()
        url_label = QLabel("Manga URL:")
        url_label.setMinimumWidth(80)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://hentai2read.com/manga/...")
        self.url_input.returnPressed.connect(self._on_add_download)
        
        self.add_button = QPushButton("Add Download")
        self.add_button.setObjectName("primary")
        self.add_button.clicked.connect(self._on_add_download)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.add_button)
        
        layout.addLayout(url_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        # Format selection
        format_label = QLabel("Format:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["images", "pdf", "cbz"])
        self.format_combo.setCurrentText("images")
        
        
        # Auto convert checkbox
        self.auto_convert_check = QCheckBox("Auto convert after download")
        
        options_layout.addWidget(format_label)
        options_layout.addWidget(self.format_combo)
        options_layout.addWidget(self.auto_convert_check)
        options_layout.addStretch()
        
        layout.addLayout(options_layout)
        
        return section
    
    def _create_queue_section(self) -> QWidget:
        """Create the download queue display section."""
        section = QFrame()
        section.setObjectName("GlassCard")
        
        layout = QVBoxLayout(section)
        
        # Queue header
        header_layout = QHBoxLayout()
        queue_label = QLabel("Download Queue")
        queue_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        
        # Control buttons
        self.pause_all_button = QPushButton("Pause All")
        self.pause_all_button.setObjectName("secondary")
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_completed_button.setObjectName("secondary")
        
        header_layout.addWidget(queue_label)
        header_layout.addStretch()
        header_layout.addWidget(self.pause_all_button)
        header_layout.addWidget(self.clear_completed_button)
        
        layout.addLayout(header_layout)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setMinimumHeight(200)
        layout.addWidget(self.queue_list)
        
        # Stats display
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Active: 0 | Queued: 0 | Completed: 0 | Failed: 0")
        self.stats_label.setObjectName("subtitle")
        
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        return section
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Download thread signals
        try:
            self.download_thread.progress_updated.disconnect(self._on_progress_updated)
        except TypeError:
            pass  # Signal was not connected
        try:
            self.download_thread.download_completed.disconnect(self._on_download_completed)
        except TypeError:
            pass  # Signal was not connected
        try:
            self.download_thread.error_occurred.disconnect(self._on_error_occurred)
        except TypeError:
            pass  # Signal was not connected
        try:
            self.download_thread.metadata_fetched.disconnect(self._on_metadata_fetched)
        except TypeError:
            pass  # Signal was not connected
        
        self.download_thread.progress_updated.connect(self._on_progress_updated)
        self.download_thread.download_completed.connect(self._on_download_completed)
        self.download_thread.error_occurred.connect(self._on_error_occurred)
        self.download_thread.metadata_fetched.connect(self._on_metadata_fetched)
        
        # Button signals (these don't need to be reconnected as they don't change)
        # They are only connected once in the constructor
    
    def _setup_signals(self) -> None:
        """Setup button signals (called once in constructor)."""
        self.pause_all_button.clicked.connect(self._on_pause_all)
        self.clear_completed_button.clicked.connect(self._on_clear_completed)
    
    def _setup_timer(self) -> None:
        """Setup the stats update timer."""
        self.stats_timer.timeout.connect(self._update_stats_display)
        self.stats_timer.start(1000)  # Update every second
    
    def _setup_drag_drop(self) -> None:
        """Setup drag and drop functionality."""
        self.drag_drop_handler = DragDropHandler(self)
        self.drag_drop_handler.urls_dropped.connect(self._on_urls_dropped)
        logger.debug("Drag and drop enabled")
    
    def _on_urls_dropped(self, urls: list) -> None:
        """
        Handle URLs dropped onto the widget.
        
        Args:
            urls: List of dropped URLs
        """
        logger.info(f"Received {len(urls)} dropped URLs")
        
        # Get current options
        options = {
            'format': self.format_combo.currentText(),
            'auto_convert': self.auto_convert_check.isChecked()
        }
        
        # Add each URL as a download task
        for url in urls:
            task_id = self.download_thread.add_download_task(url, options)
            self._add_queue_item(task_id, url)
            logger.info(f"Added dropped URL {task_id}: {url}")
        
        # Show confirmation message
        if len(urls) == 1:
            QMessageBox.information(self, "URL Added", f"Added 1 download from dropped URL.")
        else:
            QMessageBox.information(self, "URLs Added", f"Added {len(urls)} downloads from dropped URLs.")
    
    def _on_add_download(self) -> None:
        """Handle add download button click."""
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Invalid URL", "Please enter a valid manga URL.")
            return
        
        if not url.startswith("https://hentai2read.com/"):
            QMessageBox.warning(self, "Invalid URL", "URL must be from hentai2read.com")
            return
        
        # Get options
        options = {
            'format': self.format_combo.currentText(),
            'auto_convert': self.auto_convert_check.isChecked()
        }
        
        # Add to download thread and get task ID
        task_id = self.download_thread.add_download_task(url, options)
        
        # Clear input
        self.url_input.clear()
        
        # Add queue item
        self._add_queue_item(task_id, url)
        
        logger.info(f"Added download task {task_id}: {url}")
    
    def add_download_from_external(self, url: str, options: Dict[str, Any]) -> None:
        """
        Add a download from an external source (e.g., search widget).
        
        Args:
            url: Manga URL to download
            options: Download options
        """
        # Add to download thread and get task ID
        task_id = self.download_thread.add_download_task(url, options)
        
        # Add queue item
        self._add_queue_item(task_id, url)
        
        logger.info(f"Added external download task {task_id}: {url}")
    
    def _add_queue_item(self, task_id: str, url: str) -> None:
        """Add an item to the download queue display."""
        # Create queue item widget
        queue_item = QueueItemWidget(task_id, url)
        
        # Connect queue item signals
        queue_item.pause_requested.connect(self._on_item_pause_requested)
        queue_item.resume_requested.connect(self._on_item_resume_requested)
        queue_item.remove_requested.connect(self._on_item_remove_requested)
        
        # Add to list widget
        list_item = QListWidgetItem()
        list_item.setSizeHint(queue_item.sizeHint())
        
        self.queue_list.addItem(list_item)
        self.queue_list.setItemWidget(list_item, queue_item)
        
        # Store reference
        self.queue_items[task_id] = queue_item
    
    def _on_progress_updated(self, task_id: str, progress: ProgressTracking) -> None:
        """Handle progress updates from download thread."""
        if task_id in self.queue_items:
            self.queue_items[task_id].update_progress(progress)
        
        logger.debug(f"Progress update {task_id}: {progress.status} - {progress.downloaded_images}/{progress.total_images}")
    
    def _on_download_completed(self, task_id: str) -> None:
        """Handle download completion."""
        logger.info(f"Download completed: {task_id}")
        
        # Update the corresponding queue item status to completed
        if task_id in self.queue_items:
            # Create a completed progress tracking object to update the UI
            from core.models import ProgressTracking
            completed_progress = ProgressTracking(
                status="completed",
                downloaded_images=0,  # These values don't matter for completed status
                total_images=0,
                current_chapter=""
            )
            self.queue_items[task_id].update_progress(completed_progress)
            
            # Immediately update the statistics display to reflect the completed download
            self._update_stats_display()
    
    def _on_error_occurred(self, task_id: str, error: str) -> None:
        """Handle download errors."""
        logger.error(f"Download error for {task_id}: {error}")
        QMessageBox.critical(self, "Download Error", f"Error in {task_id}:\n{error}")
    
    def _on_metadata_fetched(self, url: str, metadata: MangaMetadata) -> None:
        """Handle metadata fetched from download thread."""
        # Update queue item with proper manga title
        for task_id, queue_item in self.queue_items.items():
            if queue_item.url == url:
                queue_item.set_manga_title(metadata.title)
                break
    
    def _on_item_pause_requested(self, task_id: str) -> None:
        """Handle pause request from queue item."""
        logger.info(f"Pause requested for task: {task_id}")
        # TODO: Implement pause functionality
    
    def _on_item_resume_requested(self, task_id: str) -> None:
        """Handle resume request from queue item."""
        logger.info(f"Resume requested for task: {task_id}")
        # TODO: Implement resume functionality
    
    def _on_item_remove_requested(self, task_id: str) -> None:
        """Handle remove request from queue item."""
        if task_id in self.queue_items:
            # Find and remove the list item
            for i in range(self.queue_list.count()):
                item = self.queue_list.item(i)
                widget = self.queue_list.itemWidget(item)
                if widget == self.queue_items[task_id]:
                    self.queue_list.takeItem(i)
                    break
            
            # Remove from tracking
            del self.queue_items[task_id]
            logger.info(f"Removed task: {task_id}")
    
    def _on_pause_all(self) -> None:
        """Handle pause all downloads."""
        logger.info("Pausing all downloads")
        # TODO: Implement pause all functionality
    
    def _on_clear_completed(self) -> None:
        """Handle clear completed downloads."""
        completed_tasks = []
        for task_id, queue_item in self.queue_items.items():
            if queue_item.status in ["completed", "failed"]:
                completed_tasks.append(task_id)
        
        for task_id in completed_tasks:
            self._on_item_remove_requested(task_id)
        
        logger.info(f"Cleared {len(completed_tasks)} completed downloads")
    
    def _update_stats_display(self) -> None:
        """Update the statistics display."""
        stats = self.get_download_stats()
        self.stats_label.setText(
            f"Active: {stats['active']} | "
            f"Queued: {stats['queued']} | "
            f"Completed: {stats['completed']} | "
            f"Failed: {stats['failed']}"
        )
        
        # Emit stats changed signal
        self.download_stats_changed.emit(stats)
    
    def focus_url_input(self) -> None:
        """Focus the URL input field."""
        self.url_input.setFocus()
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Update widget configuration."""
        logger.debug("Download widget config updated")
        
        # Check if we need to recreate the download thread (e.g., for settings that affect the download manager)
        recreate_thread = False
        critical_settings = ['DELETE_IMAGES_AFTER_CONVERSION', 'MAX_CONCURRENT_DOWNLOADS']
        for key in critical_settings:
            if key in config_updates:
                recreate_thread = True
                break
        
        if recreate_thread:
            # Stop the current download thread
            if self.download_thread and self.download_thread.isRunning():
                self.download_thread.stop_downloads()
                self.download_thread.wait()
            
            # Create a new download thread
            self.download_thread = DownloadWorkerThread()
            
            # Reconnect signals
            self._connect_signals()
        
        logger.debug("Download widget config updated")
    
    def get_download_stats(self) -> Dict[str, Any]:
        """Get current download statistics."""
        stats = {'active': 0, 'queued': 0, 'completed': 0, 'failed': 0, 'total_speed': 0.0}
        
        for queue_item in self.queue_items.values():
            status = queue_item.status
            if status in ["downloading", "converting"]:
                stats['active'] += 1
            elif status in ["queued", "pending"]:
                stats['queued'] += 1
            elif status == "completed":
                stats['completed'] += 1
            elif status == "failed":
                stats['failed'] += 1
        
        return stats
    
    def closeEvent(self, a0):
        """Handle widget close event."""
        self.download_thread.stop_downloads()
        super().closeEvent(a0)
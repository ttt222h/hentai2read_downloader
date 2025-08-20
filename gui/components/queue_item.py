"""
Download Queue Item Widget

Individual item widget for the download queue display.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QPushButton, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from loguru import logger
from core.models import ProgressTracking


class QueueItemWidget(QFrame):
    """
    Widget representing a single download item in the queue.
    
    Displays manga info, progress, and control buttons.
    """
    
    # Signals
    pause_requested = pyqtSignal(str)    # task_id
    resume_requested = pyqtSignal(str)   # task_id
    remove_requested = pyqtSignal(str)   # task_id
    
    def __init__(self, task_id: str, url: str, manga_title: str = None, parent: Optional[QWidget] = None):
        """
        Initialize the queue item widget.
        
        Args:
            task_id: Unique task identifier
            url: Manga URL
            manga_title: Display name for the manga
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.task_id = task_id
        self.url = url
        self.manga_title = manga_title or self._extract_title_from_url(url)
        self.status = "queued"
        self.is_paused = False
        
        self._setup_ui()
        self._connect_signals()
        
        logger.debug(f"Created queue item for task {task_id}")
    
    def _setup_ui(self) -> None:
        """Setup the queue item UI."""
        self.setObjectName("QueueItem")
        self.setFixedHeight(80)
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Info section
        info_layout = self._create_info_section()
        layout.addLayout(info_layout, 3)
        
        # Progress section
        progress_layout = self._create_progress_section()
        layout.addLayout(progress_layout, 2)
        
        # Control section
        control_layout = self._create_control_section()
        layout.addLayout(control_layout, 1)
    
    def _create_info_section(self) -> QVBoxLayout:
        """Create the info section with manga title and URL."""
        layout = QVBoxLayout()
        
        # Manga title
        self.title_label = QLabel(self.manga_title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.title_label.setWordWrap(True)
        
        # URL (truncated)
        url_display = self.url if len(self.url) <= 50 else self.url[:47] + "..."
        self.url_label = QLabel(url_display)
        self.url_label.setObjectName("subtitle")
        self.url_label.setToolTip(self.url)
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.url_label)
        
        return layout
    
    def _create_progress_section(self) -> QVBoxLayout:
        """Create the progress section with status and progress bar."""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("Queued")
        self.status_label.setFont(QFont("Segoe UI", 9))
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(20)
        
        # Progress text
        self.progress_text = QLabel("")
        self.progress_text.setObjectName("subtitle")
        self.progress_text.setVisible(False)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.progress_text)
        
        return layout
    
    def _create_control_section(self) -> QVBoxLayout:
        """Create the control section with action buttons."""
        layout = QVBoxLayout()
        
        # Pause/Resume button
        self.pause_button = QPushButton("Pause")
        self.pause_button.setObjectName("secondary")
        self.pause_button.setMaximumWidth(80)
        self.pause_button.setEnabled(False)  # Disabled until download starts
        
        # Remove button
        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("danger")
        self.remove_button.setMaximumWidth(80)
        
        layout.addWidget(self.pause_button)
        layout.addWidget(self.remove_button)
        
        return layout
    
    def _connect_signals(self) -> None:
        """Connect button signals."""
        self.pause_button.clicked.connect(self._on_pause_clicked)
        self.remove_button.clicked.connect(self._on_remove_clicked)
    
    def _extract_title_from_url(self, url: str) -> str:
        """
        Extract manga title from URL.
        
        Args:
            url: Manga URL
            
        Returns:
            Extracted title
        """
        try:
            # Extract the last part of the URL and format it
            title = url.rstrip('/').split('/')[-1]
            title = title.replace('-', ' ').title()
            return title
        except Exception:
            return "Unknown Manga"
    
    def update_progress(self, progress: ProgressTracking) -> None:
        """
        Update the progress display.
        
        Args:
            progress: Progress tracking object
        """
        self.status = progress.status
        
        # Update status label
        status_text = progress.status.title()
        if progress.current_chapter:
            status_text += f" - {progress.current_chapter}"
        self.status_label.setText(status_text)
        
        # Update progress bar
        if progress.status in ["downloading", "converting"]:
            self.progress_bar.setVisible(True)
            self.progress_text.setVisible(True)
            
            if progress.total_images > 0:
                percentage = int((progress.downloaded_images / progress.total_images) * 100)
                self.progress_bar.setValue(percentage)
                self.progress_text.setText(f"{progress.downloaded_images}/{progress.total_images} images")
            else:
                self.progress_bar.setRange(0, 0)  # Indeterminate progress
                self.progress_text.setText("Processing...")
        else:
            self.progress_bar.setVisible(False)
            self.progress_text.setVisible(False)
        
        # Update button states
        self._update_button_states()
        
        # Update styling based on status
        self._update_status_styling()
    
    def _update_button_states(self) -> None:
        """Update button enabled/disabled states based on status."""
        if self.status in ["downloading", "converting"]:
            self.pause_button.setEnabled(True)
            self.pause_button.setText("Resume" if self.is_paused else "Pause")
        elif self.status in ["queued", "pending"]:
            self.pause_button.setEnabled(False)
            self.pause_button.setText("Pause")
        else:
            self.pause_button.setEnabled(False)
            self.pause_button.setText("Pause")
    
    def _update_status_styling(self) -> None:
        """Update widget styling based on status."""
        if self.status == "completed":
            self.setStyleSheet("QueueItemWidget { border-left: 3px solid #4CAF50; }")
        elif self.status == "failed":
            self.setStyleSheet("QueueItemWidget { border-left: 3px solid #F44336; }")
        elif self.status in ["downloading", "converting"]:
            self.setStyleSheet("QueueItemWidget { border-left: 3px solid #2196F3; }")
        else:
            self.setStyleSheet("QueueItemWidget { border-left: 3px solid #9E9E9E; }")
    
    def _on_pause_clicked(self) -> None:
        """Handle pause/resume button click."""
        if self.is_paused:
            self.resume_requested.emit(self.task_id)
            self.is_paused = False
        else:
            self.pause_requested.emit(self.task_id)
            self.is_paused = True
        
        self._update_button_states()
    
    def _on_remove_clicked(self) -> None:
        """Handle remove button click."""
        self.remove_requested.emit(self.task_id)
    
    def set_manga_title(self, title: str) -> None:
        """
        Update the manga title display.
        
        Args:
            title: New manga title
        """
        self.manga_title = title
        self.title_label.setText(title)
    
    def get_task_info(self) -> Dict[str, Any]:
        """
        Get task information.
        
        Returns:
            Dictionary with task information
        """
        return {
            'task_id': self.task_id,
            'url': self.url,
            'manga_title': self.manga_title,
            'status': self.status,
            'is_paused': self.is_paused
        }
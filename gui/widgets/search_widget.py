"""
Search Widget

This module provides the manga search interface for finding
and selecting manga from hentai2read.
"""

from typing import Optional, Dict, Any, List
import asyncio
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QGridLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont

from loguru import logger
from core.config import Settings
from core.models import MangaMetadata
from scraper.hentai2read import Hentai2ReadScraper
from scraper.session import HTTPSession


class SearchWorker(QThread):
    """
    Background worker thread for performing manga searches.
    """
    
    # Signals
    search_completed = pyqtSignal(list)  # List of MangaMetadata
    search_error = pyqtSignal(str)  # Error message
    search_progress = pyqtSignal(str)  # Progress message
    
    def __init__(self, query: str):
        """
        Initialize search worker.
        
        Args:
            query: Search query string
        """
        super().__init__()
        self.query = query
        self.session = None
        self.scraper = None
    
    def run(self) -> None:
        """Run the search operation."""
        try:
            self.search_progress.emit(f"Searching for: '{self.query}'...")
            
            # Create async event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                results = loop.run_until_complete(self._perform_search())
                self.search_completed.emit(results)
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            self.search_error.emit(str(e))
    
    async def _perform_search(self) -> List[MangaMetadata]:
        """Perform the actual search operation."""
        self.session = HTTPSession()
        self.scraper = Hentai2ReadScraper(self.session)
        
        try:
            results = await self.scraper.search_manga(self.query)
            return results
        finally:
            if self.session:
                await self.session.close()


class MangaResultCard(QFrame):
    """
    Individual manga result card for search results.
    """
    
    # Signals
    download_requested = pyqtSignal(str, str)  # URL, title
    
    def __init__(self, manga: MangaMetadata, parent: Optional[QWidget] = None):
        """
        Initialize manga result card.
        
        Args:
            manga: Manga metadata
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.manga = manga
        self.setObjectName("MangaResultCard")
        self.setFixedHeight(120)
        
        self._setup_ui()
        self._apply_styling()
    
    def _setup_ui(self) -> None:
        """Setup the manga result card UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)
        
        # Thumbnail placeholder
        thumbnail_frame = QFrame()
        thumbnail_frame.setObjectName("ThumbnailFrame")
        thumbnail_frame.setFixedSize(80, 100)
        
        thumbnail_layout = QVBoxLayout(thumbnail_frame)
        thumbnail_layout.setContentsMargins(0, 0, 0, 0)
        
        thumbnail_label = QLabel("📖")
        thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumbnail_label.setStyleSheet("font-size: 32px; color: #8B949E;")
        thumbnail_layout.addWidget(thumbnail_label)
        
        layout.addWidget(thumbnail_frame)
        
        # Content area
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)
        
        # Title
        title_label = QLabel(self.manga.title)
        title_label.setObjectName("MangaTitle")
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        content_layout.addWidget(title_label)
        
        # Metadata
        chapter_count = len(self.manga.chapters) if self.manga.chapters else 0
        meta_text = f"{chapter_count} chapters"
        
        meta_label = QLabel(meta_text)
        meta_label.setObjectName("MangaMeta")
        content_layout.addWidget(meta_label)
        
        # Description (if available)
        if hasattr(self.manga, 'description') and self.manga.description:
            desc_label = QLabel(self.manga.description[:150] + "..." if len(self.manga.description) > 150 else self.manga.description)
            desc_label.setObjectName("MangaDescription")
            desc_label.setWordWrap(True)
            desc_label.setMaximumHeight(40)
            content_layout.addWidget(desc_label)
        
        content_layout.addStretch()
        layout.addLayout(content_layout, 1)
        
        # Action buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(8)
        
        download_button = QPushButton("📥 Download")
        download_button.setObjectName("primary")
        download_button.clicked.connect(self._on_download_clicked)
        
        info_button = QPushButton("ℹ️ Info")
        info_button.setObjectName("secondary")
        info_button.clicked.connect(self._on_info_clicked)
        
        button_layout.addWidget(download_button)
        button_layout.addWidget(info_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _apply_styling(self) -> None:
        """Apply styling to the manga result card."""
        self.setStyleSheet("""
            QFrame#MangaResultCard {
                background-color: rgba(22, 27, 34, 0.8);
                border: 1px solid rgba(240, 246, 252, 0.1);
                border-radius: 12px;
                margin: 4px;
            }
            
            QFrame#MangaResultCard:hover {
                border-color: #58A6FF;
                background-color: rgba(22, 27, 34, 0.9);
            }
            
            QFrame#ThumbnailFrame {
                background-color: rgba(13, 17, 23, 0.8);
                border: 1px solid rgba(240, 246, 252, 0.05);
                border-radius: 8px;
            }
            
            QLabel#MangaTitle {
                color: #F0F6FC;
                font-weight: 600;
            }
            
            QLabel#MangaMeta {
                color: #58A6FF;
                font-size: 11px;
            }
            
            QLabel#MangaDescription {
                color: #8B949E;
                font-size: 10px;
            }
        """)
    
    def _on_download_clicked(self) -> None:
        """Handle download button click."""
        self.download_requested.emit(self.manga.url, self.manga.title)
    
    def _on_info_clicked(self) -> None:
        """Handle info button click."""
        # Show detailed info dialog
        info_text = f"Title: {self.manga.title}\n"
        info_text += f"URL: {self.manga.url}\n"
        info_text += f"Chapters: {len(self.manga.chapters) if self.manga.chapters else 0}\n"
        
        if hasattr(self.manga, 'description') and self.manga.description:
            info_text += f"\nDescription:\n{self.manga.description}"
        
        QMessageBox.information(self, "Manga Information", info_text)


class SearchWidget(QWidget):
    """
    Search widget for finding manga on hentai2read.
    
    Features:
    - Search input with real-time suggestions
    - Results display in card format
    - Download integration
    - Search history
    """
    
    # Signals
    download_requested = pyqtSignal(str, dict)  # URL, options
    search_completed = pyqtSignal(int)  # Number of results
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """
        Initialize the search widget.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config = config
        self.search_worker = None
        self.current_results: List[MangaMetadata] = []
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
        logger.info("Search widget initialized")
    
    def _setup_ui(self) -> None:
        """Setup the search widget UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Header section
        header_layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔍 Search Manga")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # Search input section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter manga title to search...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setFont(QFont("Segoe UI", 12))
        
        self.search_button = QPushButton("🔍 Search")
        self.search_button.setObjectName("primary")
        self.search_button.setMinimumHeight(40)
        self.search_button.setMinimumWidth(100)
        
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(self.search_button)
        
        header_layout.addLayout(search_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        header_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Enter a search query to find manga")
        self.status_label.setObjectName("subtitle")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Results section
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(8)
        self.results_layout.addStretch()  # Push results to top
        
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll, 1)
        
        # Initial welcome message
        self._show_welcome_message()
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.search_button.clicked.connect(self._perform_search)
        self.search_input.returnPressed.connect(self._perform_search)
    
    def _show_welcome_message(self) -> None:
        """Show welcome message in results area."""
        welcome_frame = QFrame()
        welcome_frame.setObjectName("WelcomeFrame")
        welcome_layout = QVBoxLayout(welcome_frame)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setSpacing(16)
        
        # Icon
        icon_label = QLabel("🔍")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        welcome_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Search for Manga")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setObjectName("welcomeTitle")
        welcome_layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Enter a manga title in the search box above to find and download manga from hentai2read")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("welcomeDesc")
        welcome_layout.addWidget(desc_label)
        
        # Add to results layout
        self.results_layout.insertWidget(0, welcome_frame)
        
        # Apply styling
        welcome_frame.setStyleSheet("""
            QFrame#WelcomeFrame {
                background-color: rgba(22, 27, 34, 0.8);
                border: 2px dashed rgba(240, 246, 252, 0.2);
                border-radius: 16px;
                padding: 40px;
                margin: 20px;
            }
            
            QLabel#welcomeTitle {
                color: #F0F6FC;
            }
            
            QLabel#welcomeDesc {
                color: #8B949E;
                font-size: 14px;
            }
        """)
    
    def _clear_results(self) -> None:
        """Clear current search results."""
        # Remove all widgets except the last stretch
        while self.results_layout.count() > 1:
            child = self.results_layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()
        
        self.current_results.clear()
    
    def _perform_search(self) -> None:
        """Perform manga search."""
        query = self.search_input.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Search Error", "Please enter a search query.")
            return
        
        if len(query) < 2:
            QMessageBox.warning(self, "Search Error", "Search query must be at least 2 characters long.")
            return
        
        # Disable search while running
        self.search_button.setEnabled(False)
        self.search_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Searching for '{query}'...")
        
        # Clear previous results
        self._clear_results()
        
        # Start search worker
        self.search_worker = SearchWorker(query)
        self.search_worker.search_completed.connect(self._on_search_completed)
        self.search_worker.search_error.connect(self._on_search_error)
        self.search_worker.search_progress.connect(self._on_search_progress)
        self.search_worker.finished.connect(self._on_search_finished)
        self.search_worker.start()
    
    def _on_search_progress(self, message: str) -> None:
        """Handle search progress updates."""
        self.status_label.setText(message)
    
    def _on_search_completed(self, results: List[MangaMetadata]) -> None:
        """Handle search completion."""
        self.current_results = results
        
        if not results:
            self.status_label.setText("No manga found for your search query.")
            self._show_no_results_message()
        else:
            self.status_label.setText(f"Found {len(results)} manga")
            self._display_results(results)
        
        self.search_completed.emit(len(results))
    
    def _on_search_error(self, error_message: str) -> None:
        """Handle search errors."""
        self.status_label.setText("Search failed")
        QMessageBox.critical(self, "Search Error", f"Search failed: {error_message}")
        logger.error(f"Search error: {error_message}")
    
    def _on_search_finished(self) -> None:
        """Handle search worker completion."""
        # Re-enable search controls
        self.search_button.setEnabled(True)
        self.search_input.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Clean up worker
        if self.search_worker:
            self.search_worker.deleteLater()
            self.search_worker = None
    
    def _show_no_results_message(self) -> None:
        """Show no results message."""
        no_results_frame = QFrame()
        no_results_frame.setObjectName("NoResultsFrame")
        no_results_layout = QVBoxLayout(no_results_frame)
        no_results_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_results_layout.setSpacing(16)
        
        # Icon
        icon_label = QLabel("😔")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px;")
        no_results_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel("No manga found")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        message_label.setObjectName("noResultsTitle")
        no_results_layout.addWidget(message_label)
        
        # Suggestion
        suggestion_label = QLabel("Try a different search term or check your spelling")
        suggestion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        suggestion_label.setObjectName("noResultsDesc")
        no_results_layout.addWidget(suggestion_label)
        
        # Add to results layout
        self.results_layout.insertWidget(0, no_results_frame)
        
        # Apply styling
        no_results_frame.setStyleSheet("""
            QFrame#NoResultsFrame {
                background-color: rgba(22, 27, 34, 0.5);
                border: 2px dashed rgba(240, 246, 252, 0.2);
                border-radius: 16px;
                padding: 40px;
                margin: 20px;
            }
            
            QLabel#noResultsTitle {
                color: #F0F6FC;
            }
            
            QLabel#noResultsDesc {
                color: #8B949E;
                font-size: 14px;
            }
        """)
    
    def _display_results(self, results: List[MangaMetadata]) -> None:
        """Display search results."""
        for manga in results:
            card = MangaResultCard(manga)
            card.download_requested.connect(self._on_download_requested)
            self.results_layout.insertWidget(self.results_layout.count() - 1, card)
    
    def _on_download_requested(self, url: str, title: str) -> None:
        """Handle download request from result card."""
        # Create download options (will be overridden by MainWindow with actual settings)
        options = {
            'format': 'images',  # Default format
            'auto_convert': False
        }
        
        self.download_requested.emit(url, options)
        
        # Show confirmation
        QMessageBox.information(
            self,
            "Download Started",
            f"Download started for '{title}'\n\nCheck the Downloads tab for progress."
        )
    
    def focus_search_input(self) -> None:
        """Focus the search input field."""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Update widget configuration."""
        logger.debug("Search widget config updated")
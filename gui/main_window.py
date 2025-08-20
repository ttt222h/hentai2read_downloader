"""
Main Application Window

This module provides the main PyQt6 window that serves as the
primary interface for the Hentai2Read Downloader application.
"""

from typing import Optional, Dict, Any
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QCloseEvent, QResizeEvent

from loguru import logger

from core.config import Settings
from gui.widgets.navigation_bar import NavigationBar
from gui.widgets.download_widget import DownloadWidget
from gui.widgets.settings_widget import SettingsWidget
from gui.widgets.search_widget import SearchWidget
from utils.logging_config import update_logger_config


class MainWindow(QMainWindow):
    """
    Main application window with modern glass morphism design.
    
    Features:
    - Tab-based navigation system
    - Download management interface
    - Settings configuration panel
    - Search functionality
    - Responsive layout design
    """
    
    # Window signals
    download_requested = pyqtSignal(str, dict)  # URL, options
    settings_changed = pyqtSignal(dict)  # Settings dict
    window_closing = pyqtSignal()  # Window close event
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            config: Application configuration
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        self.config = config
        
        # Window properties
        self.setWindowTitle("Hentai2Read Downloader")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Initialize components
        self.navigation_bar: Optional[NavigationBar] = None
        self.download_widget: Optional[DownloadWidget] = None
        self.settings_widget: Optional[SettingsWidget] = None
        self.search_widget: Optional[SearchWidget] = None
        
        # Responsive design state
        self.is_compact_mode = False
        
        # Status tracking
        self.download_stats = {
            'active': 0,
            'queued': 0,
            'completed': 0,
            'failed': 0,
            'total_speed': 0.0
        }
        
        # Setup window
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Start status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(1000)  # Update every second
        
        logger.info("Main window initialized")
    
    def _setup_ui(self) -> None:
        """Setup the main user interface layout."""
        try:
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QVBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Create navigation bar
            self.navigation_bar = NavigationBar()
            main_layout.addWidget(self.navigation_bar)
            
            # Create tab widget for main content
            self.tab_widget = QTabWidget()
            self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
            
            # Create main content widgets
            self.download_widget = DownloadWidget()
            self.search_widget = SearchWidget(self.config)
            self.settings_widget = SettingsWidget(self.config)
            
            # Add tabs
            self.tab_widget.addTab(self.download_widget, "📥 Downloads")
            self.tab_widget.addTab(self.search_widget, "🔍 Search")
            self.tab_widget.addTab(self.settings_widget, "⚙️ Settings")
            
            # Add tab widget to main layout
            main_layout.addWidget(self.tab_widget)
            
            # Apply styling
            self._apply_styling()
            
            # Setup responsive design
            self._setup_responsive_design()
            
            logger.debug("Main UI layout created")
            
        except Exception as e:
            logger.error(f"Failed to setup UI: {e}")
            raise
    
    def _setup_menu_bar(self) -> None:
        """Setup the application menu bar."""
        try:
            menubar = self.menuBar()
            if not menubar:
                logger.error("Failed to get menu bar")
                return
            
            # File menu
            file_menu = menubar.addMenu("&File")
            if not file_menu:
                logger.error("Failed to create file menu")
                return
            
            # Add download action
            add_download_action = QAction("&Add Download", self)
            add_download_action.setShortcut(QKeySequence("Ctrl+N"))
            add_download_action.setStatusTip("Add a new download")
            add_download_action.triggered.connect(self._on_add_download)
            file_menu.addAction(add_download_action)
            
            # Search action
            search_action = QAction("&Search", self)
            search_action.setShortcut(QKeySequence("Ctrl+F"))
            search_action.setStatusTip("Search for manga")
            search_action.triggered.connect(self._on_search)
            file_menu.addAction(search_action)
            
            file_menu.addSeparator()
            
            # Exit action
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut(QKeySequence("Ctrl+Q"))
            exit_action.setStatusTip("Exit the application")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Help menu
            help_menu = menubar.addMenu("&Help")
            if help_menu:
                # About action
                about_action = QAction("&About", self)
                about_action.setStatusTip("About this application")
                about_action.triggered.connect(self._show_about)
                help_menu.addAction(about_action)
            
            logger.debug("Menu bar created")
            
        except Exception as e:
            logger.error(f"Failed to setup menu bar: {e}")
    
    def _setup_status_bar(self) -> None:
        """Setup the status bar."""
        try:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            
            # Initial status message
            self.status_bar.showMessage("Ready")
            
            logger.debug("Status bar created")
            
        except Exception as e:
            logger.error(f"Failed to setup status bar: {e}")
    
    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts."""
        try:
            # Tab switching shortcuts
            for i in range(1, 10):
                shortcut = QKeySequence(f"Ctrl+{i}")
                action = QAction(self)
                action.setShortcut(shortcut)
                action.triggered.connect(lambda checked, idx=i-1: self._switch_tab(idx))
                self.addAction(action)
            
            logger.debug("Keyboard shortcuts configured")
            
        except Exception as e:
            logger.error(f"Failed to setup shortcuts: {e}")
    
    def _connect_signals(self) -> None:
        """Connect widget signals to handlers."""
        try:
            # Navigation bar signals
            if self.navigation_bar:
                self.navigation_bar.tab_changed.connect(self._on_tab_changed)
            
            # Download widget signals
            if self.download_widget:
                self.download_widget.download_requested.connect(self.download_requested)
                self.download_widget.download_stats_changed.connect(self._update_download_stats)
            
            # Search widget signals
            if self.search_widget:
                self.search_widget.download_requested.connect(self._on_search_download_requested)
            
            # Settings widget signals
            if self.settings_widget:
                self.settings_widget.settings_changed.connect(self.settings_changed)
            
            logger.debug("Widget signals connected")
            
        except Exception as e:
            logger.error(f"Failed to connect signals: {e}")
    
    def _on_search_download_requested(self, url: str, options: dict) -> None:
        """Handle download request from search widget."""
        try:
            # Get current format and auto_convert settings from download widget
            if self.download_widget:
                # Override options with current settings from download widget UI
                current_options = {
                    'format': self.download_widget.format_combo.currentText(),
                    'auto_convert': self.download_widget.auto_convert_check.isChecked()
                }
                
                # Add the download to the download widget with current settings
                self.download_widget.add_download_from_external(url, current_options)
            
            # Also emit the main download requested signal
            self.download_requested.emit(url, options)
            
        except Exception as e:
            logger.error(f"Failed to handle search download request: {e}")
    
    def _apply_styling(self) -> None:
        """Apply custom styling to the window."""
        try:
            # Set object names for CSS targeting
            self.setObjectName("MainWindow")
            
            if self.tab_widget:
                self.tab_widget.setObjectName("MainTabWidget")
            
            logger.debug("Custom styling applied")
            
        except Exception as e:
            logger.error(f"Failed to apply styling: {e}")
    
    def _switch_tab(self, index: int) -> None:
        """Switch to the specified tab."""
        if self.tab_widget and 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def _on_tab_changed(self, tab_name: str) -> None:
        """Handle navigation bar tab changes."""
        try:
            tab_mapping = {
                "Downloads": 0,
                "Search": 1,
                "Settings": 2,
                "About": 2,  # Show about dialog instead of switching tab
            }
            
            if tab_name == "About":
                self._show_about()
            elif tab_name in tab_mapping:
                self.tab_widget.setCurrentIndex(tab_mapping[tab_name])
            
        except Exception as e:
            logger.error(f"Failed to handle tab change: {e}")
    
    def _on_add_download(self) -> None:
        """Handle add download menu action."""
        try:
            # Switch to downloads tab and focus URL input
            self.tab_widget.setCurrentIndex(0)
            if self.download_widget:
                self.download_widget.focus_url_input()
            
        except Exception as e:
            logger.error(f"Failed to handle add download: {e}")
    
    def _on_search(self) -> None:
        """Handle search menu action."""
        try:
            # Switch to search tab and focus search input
            self.tab_widget.setCurrentIndex(1)
            if self.search_widget:
                self.search_widget.focus_search_input()
            
        except Exception as e:
            logger.error(f"Failed to handle search: {e}")
    
    def _show_about(self) -> None:
        """Show about dialog."""
        try:
            about_dialog = QMessageBox(self)
            about_dialog.setWindowTitle("About Hentai2Read Downloader")
            about_dialog.setTextFormat(Qt.TextFormat.RichText)
            about_dialog.setText(
                "<h3 style='color: #F0F6FC;'>Hentai2Read Downloader v1.0.0</h3>"
                "<p style='color: #8B949E;'>A modern manga downloader with CLI and GUI interfaces.</p>"
                "<p style='color: #8B949E;'>Built with PyQt6 and modern design principles.</p>"
                "<p style='color: #F0F6FC;'><b>Features:</b></p>"
                "<ul style='color: #8B949E;'>"
                "<li>Parallel downloads with threading</li>"
                "<li>PDF and CBZ format conversion</li>"
                "<li>Glass morphism UI design</li>"
                "<li>Manga search functionality</li>"
                "</ul>"
            )
            about_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            about_dialog.exec()
            
        except Exception as e:
            logger.error(f"Failed to show about dialog: {e}")
    
    def _update_status(self) -> None:
        """Update the status bar with current information."""
        try:
            stats = self.download_stats
            
            # Format status message
            status_parts = []
            
            if stats['active'] > 0:
                status_parts.append(f"Downloading: {stats['active']}")
            
            if stats['queued'] > 0:
                status_parts.append(f"Queued: {stats['queued']}")
            
            if stats['total_speed'] > 0:
                speed_mb = stats['total_speed'] / (1024 * 1024)
                status_parts.append(f"Speed: {speed_mb:.1f} MB/s")
            
            if not status_parts:
                status_message = "Ready"
            else:
                status_message = " | ".join(status_parts)
            
            self.status_bar.showMessage(status_message)
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def _update_download_stats(self, stats: Dict[str, Any]) -> None:
        """Update download statistics."""
        try:
            self.download_stats.update(stats)
            
        except Exception as e:
            logger.error(f"Failed to update download stats: {e}")
    
    
    def on_config_updated(self, config_updates: Dict[str, Any]) -> None:
        """Handle configuration updates."""
        try:
            logger.info("Configuration updated")
            
            # Update the global settings instance
            from core.config import settings
            for key, value in config_updates.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            # Update widgets with new configuration
            if self.download_widget:
                self.download_widget.update_config(config_updates)
            
            if self.settings_widget:
                self.settings_widget.update_config(config_updates)
            
            if self.search_widget:
                self.search_widget.update_config(config_updates)
            
            # Update logger configuration
            update_logger_config(settings)
            
        except Exception as e:
            logger.error(f"Failed to handle config update: {e}")
    
    def closeEvent(self, a0: Optional[QCloseEvent]) -> None:
        """Handle window close event."""
        try:
            # Emit closing signal
            self.window_closing.emit()
            
            # Stop timers
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
            
            logger.info("Main window closing")
            if a0 is not None:
                a0.accept()
            
        except Exception as e:
            logger.error(f"Error during window close: {e}")
            if a0 is not None:
                a0.accept()  # Close anyway
    
    def _setup_responsive_design(self) -> None:
        """Setup responsive design features."""
        try:
            # Check initial window size and adjust layout
            self._check_responsive_breakpoints()
            
            logger.debug("Responsive design setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup responsive design: {e}")
    
    def _check_responsive_breakpoints(self) -> None:
        """Check window size and apply responsive design changes."""
        try:
            window_width = self.width()
            window_height = self.height()
            
            # Responsive breakpoints
            COMPACT_WIDTH = 1000
            DENSE_HEIGHT = 600
            
            # Check for compact mode
            should_be_compact = window_width < COMPACT_WIDTH
            
            if should_be_compact != self.is_compact_mode:
                self.is_compact_mode = should_be_compact
                self._apply_responsive_layout()
            
            logger.debug(f"Responsive check: {window_width}x{window_height}, compact: {self.is_compact_mode}")
            
        except Exception as e:
            logger.error(f"Failed to check responsive breakpoints: {e}")
    
    def _apply_responsive_layout(self) -> None:
        """Apply responsive layout changes based on current mode."""
        try:
            if self.is_compact_mode:
                # Compact mode: reduce spacing and padding
                if self.navigation_bar:
                    self.navigation_bar.setFixedHeight(56)  # Slightly smaller
            else:
                # Normal mode: standard spacing
                if self.navigation_bar:
                    self.navigation_bar.setFixedHeight(64)
            
            logger.debug(f"Applied responsive layout: compact={self.is_compact_mode}")
            
        except Exception as e:
            logger.error(f"Failed to apply responsive layout: {e}")
    
    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        """Handle window resize events for responsive design."""
        try:
            if a0 is not None:
                super().resizeEvent(a0)
            
            # Check responsive breakpoints on resize
            self._check_responsive_breakpoints()
            
        except Exception as e:
            logger.error(f"Failed to handle resize event: {e}")
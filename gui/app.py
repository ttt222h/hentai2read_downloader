"""
Main GUI Application Entry Point

This module provides the main PyQt6 application class that initializes
the GUI interface and manages the application lifecycle.
"""

import sys
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from loguru import logger

from core.config import Settings
from gui.main_window import MainWindow
from gui.themes.dark_theme import DarkTheme
from utils.logging_config import configure_logger


class GuiApplication(QApplication):
    """
    Main GUI Application class that manages the PyQt6 application lifecycle.
    
    Features:
    - Theme management and styling
    - Font loading and configuration
    - Window state management
    - Signal/slot architecture setup
    - Performance monitoring
    """
    
    # Application-wide signals
    config_updated = pyqtSignal(dict) # Configuration changes
    
    def __init__(self, argv: list[str], config: Optional[Settings] = None):
        """
        Initialize the GUI application.
        
        Args:
            argv: Command line arguments
            config: Application configuration (optional)
        """
        super().__init__(argv)
        
        # Store configuration
        self.config = config or Settings()
        
        # Application properties
        self.setApplicationName("Hentai2Read Downloader")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("H2R Downloader")
        self.setOrganizationDomain("hentai2read-downloader.local")
        
        # Initialize components
        self.main_window: Optional[MainWindow] = None
        self.theme = DarkTheme()
        
        # Setup application
        self._setup_fonts()
        self._setup_theme()
        self._setup_icon()
        
        # Configure logger based on settings
        configure_logger(self.config)
        
        logger.info("GUI Application initialized")
    
    def _setup_fonts(self) -> None:
        """Load and configure application fonts."""
        try:
            # Set default application font
            default_font = QFont("Inter", 10)
            if not default_font.exactMatch():
                # Fallback to system fonts
                default_font = QFont("Segoe UI", 10)  # Windows
                if not default_font.exactMatch():
                    default_font = QFont("SF Pro Display", 10)  # macOS
                    if not default_font.exactMatch():
                        default_font = QFont("Ubuntu", 10)  # Linux
            
            self.setFont(default_font)
            logger.debug(f"Application font set to: {default_font.family()}")
            
        except Exception as e:
            logger.warning(f"Failed to setup fonts: {e}")
    
    def _setup_theme(self) -> None:
        """Apply the application theme and styling."""
        try:
            # Apply dark theme stylesheet
            stylesheet = self.theme.get_stylesheet()
            self.setStyleSheet(stylesheet)
            
            logger.debug("Dark theme applied successfully")
            
        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
    
    def _setup_icon(self) -> None:
        """Set the application icon."""
        try:
            # Look for application icon
            icon_path = Path(__file__).parent.parent / "assets" / "icons" / "app_icon.png"
            
            if icon_path.exists():
                icon = QIcon(str(icon_path))
                self.setWindowIcon(icon)
                logger.debug(f"Application icon loaded from: {icon_path}")
            else:
                logger.warning(f"Application icon not found at: {icon_path}")
                
        except Exception as e:
            logger.warning(f"Failed to load application icon: {e}")
    
    def create_main_window(self) -> MainWindow:
        """
        Create and configure the main application window.
        
        Returns:
            MainWindow: The main application window instance
        """
        if self.main_window is None:
            self.main_window = MainWindow(self.config)
            
            # Connect application-wide signals
            self.config_updated.connect(self.main_window.on_config_updated)
            
            # Connect main window signals to application signals
            self.main_window.settings_changed.connect(self.config_updated)
            
            # Configure window with default size
            self.main_window.resize(1400, 900)
            
            logger.info("Main window created and configured")
        
        return self.main_window
    
    def show_main_window(self) -> None:
        """Show the main application window."""
        if self.main_window is None:
            self.create_main_window()
        
        # At this point main_window is guaranteed to be not None
        if self.main_window is not None:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
        
        logger.info("Main window displayed")
    
    def change_theme(self, theme_name: str) -> None:
        """
        Change the application theme.
        
        Args:
            theme_name: Name of the theme to apply
        """
        try:
            # Only dark theme is supported
            self.theme = DarkTheme()
            
            # Apply dark theme
            stylesheet = self.theme.get_stylesheet()
            self.setStyleSheet(stylesheet)
            
            logger.info("Dark theme applied")
            
        except Exception as e:
            logger.error(f"Failed to apply theme: {e}")
    
    def update_config(self, new_config: dict) -> None:
        """
        Update application configuration.
        
        Args:
            new_config: Dictionary of configuration updates
        """
        try:
            # Update configuration
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Also update the global settings instance
            from core.config import settings
            for key, value in new_config.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            # Emit configuration updated signal
            self.config_updated.emit(new_config)
            
            # Reconfigure logger with updated settings
            configure_logger(self.config)
            
            logger.info("Application configuration updated")
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
    
    def cleanup(self) -> None:
        """Cleanup resources before application exit."""
        try:
            if self.main_window:
                # Close main window
                self.main_window.close()
            
            logger.info("GUI Application cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


def run_gui(config: Optional[Settings] = None) -> int:
    """
    Run the GUI application.
    
    Args:
        config: Application configuration (optional)
        
    Returns:
        int: Application exit code
    """
    try:
        # Create application instance
        app = GuiApplication(sys.argv, config)
        
        # Create and show main window
        app.show_main_window()
        
        # Setup cleanup on exit
        app.aboutToQuit.connect(app.cleanup)
        
        # Run application event loop
        exit_code = app.exec()
        
        logger.info(f"GUI Application exited with code: {exit_code}")
        return exit_code
        
    except Exception as e:
        logger.error(f"Failed to run GUI application: {e}")
        return 1


if __name__ == "__main__":
    # Run GUI application directly
    exit_code = run_gui()
    sys.exit(exit_code)
"""
Path Selection Dialog Component

Reusable component for selecting files and directories.
"""

from typing import Optional, List
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, 
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal

from loguru import logger


class PathSelector(QWidget):
    """
    Path selection widget with browse button.
    
    Provides a text input field with a browse button for
    selecting files or directories.
    """
    
    # Signals
    path_changed = pyqtSignal(str)  # New path selected
    
    def __init__(self, 
                 mode: str = "directory",
                 placeholder: str = "",
                 button_text: str = "Browse...",
                 parent: Optional[QWidget] = None):
        """
        Initialize the path selector.
        
        Args:
            mode: Selection mode ("directory", "file", "files")
            placeholder: Placeholder text for input field
            button_text: Text for browse button
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.mode = mode
        self.file_filters = "All Files (*)"
        
        self._setup_ui(placeholder, button_text)
        self._connect_signals()
    
    def _setup_ui(self, placeholder: str, button_text: str) -> None:
        """Setup the path selector UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Path input field
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(placeholder)
        
        # Browse button
        self.browse_button = QPushButton(button_text)
        self.browse_button.setMaximumWidth(100)
        
        layout.addWidget(self.path_input)
        layout.addWidget(self.browse_button)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        self.path_input.textChanged.connect(self._on_path_changed)
        self.browse_button.clicked.connect(self._on_browse_clicked)
    
    def _on_path_changed(self, text: str) -> None:
        """Handle path input change."""
        self.path_changed.emit(text)
    
    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        try:
            current_path = self.path_input.text() or str(Path.home())
            
            if self.mode == "directory":
                selected_path = QFileDialog.getExistingDirectory(
                    self,
                    "Select Directory",
                    current_path
                )
            elif self.mode == "file":
                selected_path, _ = QFileDialog.getOpenFileName(
                    self,
                    "Select File",
                    current_path,
                    self.file_filters
                )
            elif self.mode == "files":
                selected_paths, _ = QFileDialog.getOpenFileNames(
                    self,
                    "Select Files",
                    current_path,
                    self.file_filters
                )
                selected_path = ";".join(selected_paths) if selected_paths else ""
            else:
                logger.error(f"Unknown path selector mode: {self.mode}")
                return
            
            if selected_path:
                self.path_input.setText(selected_path)
                
        except Exception as e:
            logger.error(f"Error in path selection: {e}")
            QMessageBox.critical(self, "Error", f"Failed to select path:\n{e}")
    
    def set_path(self, path: str) -> None:
        """
        Set the current path.
        
        Args:
            path: Path to set
        """
        self.path_input.setText(path)
    
    def get_path(self) -> str:
        """
        Get the current path.
        
        Returns:
            Current path string
        """
        return self.path_input.text()
    
    def set_file_filters(self, filters: str) -> None:
        """
        Set file filters for file selection.
        
        Args:
            filters: File filter string (e.g., "Images (*.png *.jpg);;All Files (*)")
        """
        self.file_filters = filters
    
    def validate_path(self) -> bool:
        """
        Validate the current path.
        
        Returns:
            True if path is valid
        """
        path_str = self.get_path()
        if not path_str:
            return False
        
        try:
            path = Path(path_str)
            
            if self.mode == "directory":
                return path.exists() and path.is_dir()
            elif self.mode in ["file", "files"]:
                if self.mode == "files" and ";" in path_str:
                    # Multiple files
                    paths = [Path(p.strip()) for p in path_str.split(";")]
                    return all(p.exists() and p.is_file() for p in paths)
                else:
                    # Single file
                    return path.exists() and path.is_file()
            
        except Exception as e:
            logger.debug(f"Path validation error: {e}")
            return False
        
        return False
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Enable or disable the path selector.
        
        Args:
            enabled: Whether to enable the widget
        """
        self.path_input.setEnabled(enabled)
        self.browse_button.setEnabled(enabled)
    
    def clear(self) -> None:
        """Clear the path input."""
        self.path_input.clear()


class DirectorySelector(PathSelector):
    """Specialized directory selector."""
    
    def __init__(self, 
                 placeholder: str = "Select directory...",
                 parent: Optional[QWidget] = None):
        """Initialize directory selector."""
        super().__init__(
            mode="directory",
            placeholder=placeholder,
            button_text="Browse...",
            parent=parent
        )


class FileSelector(PathSelector):
    """Specialized file selector."""
    
    def __init__(self, 
                 placeholder: str = "Select file...",
                 file_filters: str = "All Files (*)",
                 parent: Optional[QWidget] = None):
        """Initialize file selector."""
        super().__init__(
            mode="file",
            placeholder=placeholder,
            button_text="Browse...",
            parent=parent
        )
        self.set_file_filters(file_filters)


class MultiFileSelector(PathSelector):
    """Specialized multiple file selector."""
    
    def __init__(self, 
                 placeholder: str = "Select files...",
                 file_filters: str = "All Files (*)",
                 parent: Optional[QWidget] = None):
        """Initialize multiple file selector."""
        super().__init__(
            mode="files",
            placeholder=placeholder,
            button_text="Browse...",
            parent=parent
        )
        self.set_file_filters(file_filters)
    
    def get_paths(self) -> List[str]:
        """
        Get list of selected file paths.
        
        Returns:
            List of file paths
        """
        path_str = self.get_path()
        if not path_str:
            return []
        
        if ";" in path_str:
            return [p.strip() for p in path_str.split(";")]
        else:
            return [path_str]
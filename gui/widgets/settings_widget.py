"""
Settings Configuration Widget

This module provides the settings interface for configuring
application preferences and options.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QComboBox, QFrame,
    QSpinBox, QTabWidget, QFileDialog, QMessageBox,
    QScrollArea, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from loguru import logger
from core.config import Settings, settings
from gui.components.settings_tabs import GeneralSettingsTab, PerformanceSettingsTab, AdvancedSettingsTab
from utils.logging_config import update_logger_config


class SettingsWidget(QWidget):
    """
    Settings configuration widget with tabbed interface.
    
    Provides comprehensive settings management including:
    - General application settings
    - Performance and download options
    - Advanced configuration
    """
    
    # Signals
    settings_changed = pyqtSignal(dict)  # Settings updates
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """
        Initialize the settings widget.
        
        Args:
            config: Application configuration
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config = config
        self.pending_changes = {}  # Track unsaved changes
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        self._load_current_settings()
        
        logger.info("Settings widget initialized")
    
    def _setup_ui(self) -> None:
        """Setup the complete settings interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("⚙️ Application Settings")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        
        # Create tabs
        self.general_tab = GeneralSettingsTab(self.config)
        self.performance_tab = PerformanceSettingsTab(self.config)
        self.advanced_tab = AdvancedSettingsTab(self.config)
        
        # Add tabs
        self.tab_widget.addTab(self.general_tab, "📁 General")
        self.tab_widget.addTab(self.performance_tab, "🚀 Performance")
        self.tab_widget.addTab(self.advanced_tab, "🔧 Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.reset_button = QPushButton("Reset to Defaults")
        self.reset_button.setObjectName("secondary")
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondary")
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.setObjectName("primary")
        self.apply_button.setEnabled(False)  # Disabled until changes made
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.setObjectName("primary")
        
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Tab change tracking
        for tab in [self.general_tab, self.performance_tab, self.advanced_tab]:
            tab.setting_changed.connect(self._on_setting_changed)
        
        # Button signals
        self.reset_button.clicked.connect(self._on_reset_defaults)
        self.cancel_button.clicked.connect(self._on_cancel_changes)
        self.apply_button.clicked.connect(self._on_apply_changes)
        self.save_button.clicked.connect(self._on_save_settings)
    
    def _load_current_settings(self) -> None:
        """Load current settings into the UI."""
        try:
            # Load settings into each tab
            self.general_tab.load_settings(self.config)
            self.performance_tab.load_settings(self.config)
            self.advanced_tab.load_settings(self.config)
            
            logger.debug("Current settings loaded into UI")
            
        except Exception as e:
            logger.error(f"Failed to load current settings: {e}")
    
    def _on_setting_changed(self, setting_name: str, value: Any) -> None:
        """Handle setting change from tabs."""
        self.pending_changes[setting_name] = value
        self.apply_button.setEnabled(len(self.pending_changes) > 0)
        
        logger.debug(f"Setting changed: {setting_name} = {value}")
    
    def _on_reset_defaults(self) -> None:
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Create default settings
                default_settings = Settings()
                
                # Load defaults into tabs
                self.general_tab.load_settings(default_settings)
                self.performance_tab.load_settings(default_settings)
                self.advanced_tab.load_settings(default_settings)
                
                # Clear pending changes
                self.pending_changes.clear()
                self.apply_button.setEnabled(False)
                
                QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults.")
                logger.info("Settings reset to defaults")
                
            except Exception as e:
                logger.error(f"Failed to reset settings: {e}")
                QMessageBox.critical(self, "Error", f"Failed to reset settings:\n{e}")
    
    def _on_cancel_changes(self) -> None:
        """Cancel pending changes."""
        if self.pending_changes:
            reply = QMessageBox.question(
                self,
                "Cancel Changes",
                "You have unsaved changes. Are you sure you want to cancel?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._load_current_settings()
                self.pending_changes.clear()
                self.apply_button.setEnabled(False)
                logger.info("Settings changes cancelled")
    
    def _on_apply_changes(self) -> None:
        """Apply pending changes without saving."""
        try:
            if not self.pending_changes:
                return
            
            # Validate changes
            validation_errors = self._validate_settings()
            if validation_errors:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Please fix the following errors:\n" + "\n".join(validation_errors)
                )
                return
            
            # Apply changes to config
            for setting_name, value in self.pending_changes.items():
                setattr(self.config, setting_name, value)
            
            # Emit settings changed signal
            self.settings_changed.emit(self.pending_changes.copy())
            
            # Clear pending changes
            self.pending_changes.clear()
            self.apply_button.setEnabled(False)
            
            # Update logger configuration
            update_logger_config(self.config)
            
            QMessageBox.information(self, "Settings Applied", "Settings have been applied successfully.")
            logger.info("Settings changes applied")
            
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to apply settings:\n{e}")
    
    def _on_save_settings(self) -> None:
        """Save settings to file."""
        try:
            # Apply any pending changes first
            if self.pending_changes:
                self._on_apply_changes()
                if self.pending_changes:  # If apply failed
                    return
            
            # Save to file
            self.config.save_to_env()
            
            # Update logger configuration
            update_logger_config(self.config)
            
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully.")
            logger.info("Settings saved to file")
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save settings:\n{e}")
    
    def _validate_settings(self) -> list:
        """
        Validate pending settings changes.
        
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            # Validate download directory
            if 'DOWNLOAD_DIR' in self.pending_changes:
                path = Path(self.pending_changes['DOWNLOAD_DIR'])
                if not path.parent.exists():
                    errors.append("Download directory parent does not exist")
            
            # Validate concurrent downloads
            if 'MAX_CONCURRENT_DOWNLOADS' in self.pending_changes:
                value = self.pending_changes['MAX_CONCURRENT_DOWNLOADS']
                if not isinstance(value, int) or value < 1 or value > 16:
                    errors.append("Max concurrent downloads must be between 1 and 16")
            
            # Add more validation as needed
            
        except Exception as e:
            errors.append(f"Validation error: {e}")
        
        return errors
    
    def update_config(self, config_updates: Dict[str, Any]) -> None:
        """Update widget configuration."""
        try:
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            # Also update the global settings instance
            from core.config import settings
            for key, value in config_updates.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            
            # Reload settings in UI
            self._load_current_settings()
            
            # Update logger configuration
            update_logger_config(self.config)
            
            logger.debug("Settings widget config updated")
            
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
    
    def get_current_settings(self) -> Dict[str, Any]:
        """
        Get current settings from all tabs.
        
        Returns:
            Dictionary of current settings
        """
        settings_dict = {}
        
        try:
            # Collect settings from all tabs
            settings_dict.update(self.general_tab.get_settings())
            settings_dict.update(self.performance_tab.get_settings())
            settings_dict.update(self.advanced_tab.get_settings())
            
        except Exception as e:
            logger.error(f"Failed to get current settings: {e}")
        
        return settings_dict
    
    def has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return len(self.pending_changes) > 0
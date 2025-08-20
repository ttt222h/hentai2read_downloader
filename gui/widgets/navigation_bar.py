"""
Navigation Bar Widget

This module provides a modern tab-based navigation bar with
glass morphism styling and smooth animations.
"""

from typing import List, Optional
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, 
    QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPainter, QPen, QColor

from loguru import logger


class NavigationTab(QPushButton):
    """
    Custom navigation tab button with modern styling.
    
    Features:
    - Glass morphism appearance
    - Hover and active state animations
    - Icon and text support
    - Smooth transitions
    """
    
    def __init__(self, text: str, icon: str = "", parent: Optional[QWidget] = None):
        """
        Initialize navigation tab.
        
        Args:
            text: Tab display text
            icon: Tab icon (emoji or icon font)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.tab_text = text
        self.tab_icon = icon
        self.is_active = False
        
        # Setup button
        self.setCheckable(True)
        self.setMinimumHeight(48)
        self.setMinimumWidth(120)
        
        # Set button text with icon
        display_text = f"{icon} {text}" if icon else text
        self.setText(display_text)
        
        # Apply styling
        self.setObjectName("NavigationTab")
        self._apply_styling()
        
        logger.debug(f"Navigation tab created: {text}")
    
    def _apply_styling(self) -> None:
        """Apply custom styling to the tab."""
        try:
            self.setStyleSheet(f"""
                QPushButton#NavigationTab {{
                    background-color: transparent;
                    border: 1px solid rgba(240, 246, 252, 0.1);
                    border-radius: 8px;
                    color: #8B949E;
                    font-weight: 500;
                    font-size: 11px;
                    padding: 8px 16px;
                    margin: 4px 2px;
                    text-align: center;
                }}
                
                QPushButton#NavigationTab:hover {{
                    background-color: rgba(88, 166, 255, 0.1);
                    border-color: #58A6FF;
                    color: #F0F6FC;
                }}
                
                QPushButton#NavigationTab:checked {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #58A6FF,
                        stop:1 #1F6FEB);
                    border-color: #58A6FF;
                    color: white;
                    font-weight: 600;
                }}
                
                QPushButton#NavigationTab:pressed {{
                    background-color: rgba(88, 166, 255, 0.2);
                }}
            """)
            
        except Exception as e:
            logger.error(f"Failed to apply tab styling: {e}")
    
    def set_active(self, active: bool) -> None:
        """
        Set the active state of the tab.
        
        Args:
            active: Whether the tab should be active
        """
        self.is_active = active
        self.setChecked(active)


class NavigationBar(QWidget):
    """
    Modern navigation bar with tab-based navigation.
    
    Features:
    - Glass morphism background
    - Animated tab switching
    - Responsive design
    - Keyboard navigation support
    """
    
    # Signals
    tab_changed = pyqtSignal(str)  # Tab name
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the navigation bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Tab configuration
        self.tabs_config = [
            {"name": "Downloads", "icon": "📥", "tooltip": "Manage downloads", "shortcut": "Ctrl+1"},
            {"name": "Settings", "icon": "⚙️", "tooltip": "Application settings", "shortcut": "Ctrl+2"},
            {"name": "Search", "icon": "🔍", "tooltip": "Search for manga", "shortcut": "Ctrl+3"},
            {"name": "About", "icon": "❓", "tooltip": "About this application", "shortcut": "Ctrl+4"},
        ]
        
        # State tracking
        self.tabs: List[NavigationTab] = []
        self.active_tab_index = 0
        
        # Setup UI
        self.setFixedHeight(64)
        self._setup_ui()
        self._apply_styling()
        
        # Set initial active tab
        self._set_active_tab(0)
        
        logger.info("Navigation bar initialized")
    
    def _setup_ui(self) -> None:
        """Setup the navigation bar UI."""
        try:
            # Main layout
            layout = QHBoxLayout(self)
            layout.setContentsMargins(16, 8, 16, 8)
            layout.setSpacing(4)
            
            # Application title/logo area
            title_label = QLabel("Hentai2Read Downloader")
            title_label.setObjectName("AppTitle")
            title_label.setFont(QFont("Inter", 12, QFont.Weight.Bold))
            layout.addWidget(title_label)
            
            # Spacer to push tabs to center
            layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            
            # Create navigation tabs
            for i, tab_config in enumerate(self.tabs_config):
                tab = NavigationTab(
                    text=tab_config["name"],
                    icon=tab_config["icon"],
                    parent=self
                )
                
                # Set tooltip
                tab.setToolTip(tab_config["tooltip"])
                
                # Connect click signal
                tab.clicked.connect(lambda checked, idx=i: self._on_tab_clicked(idx))
                
                # Add to layout and list
                layout.addWidget(tab)
                self.tabs.append(tab)
            
            # Spacer for right side
            layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            
            # Status indicator (optional)
            status_indicator = QLabel("●")
            status_indicator.setObjectName("StatusIndicator")
            status_indicator.setToolTip("Application status")
            layout.addWidget(status_indicator)
            
            logger.debug("Navigation bar UI created")
            
        except Exception as e:
            logger.error(f"Failed to setup navigation bar UI: {e}")
            raise
    
    def _apply_styling(self) -> None:
        """Apply styling to the navigation bar."""
        try:
            self.setObjectName("NavigationBar")
            self.setStyleSheet(f"""
                QWidget#NavigationBar {{
                    background-color: rgba(22, 27, 34, 0.95);
                    border-bottom: 1px solid rgba(240, 246, 252, 0.1);
                    backdrop-filter: blur(20px);
                }}
                
                QLabel#AppTitle {{
                    color: #F0F6FC;
                    font-weight: 600;
                    font-size: 14px;
                    padding: 8px 0px;
                }}
                
                QLabel#StatusIndicator {{
                    color: #3FB950;
                    font-size: 16px;
                    padding: 4px;
                }}
            """)
            
        except Exception as e:
            logger.error(f"Failed to apply navigation bar styling: {e}")
    
    def _on_tab_clicked(self, index: int) -> None:
        """
        Handle tab click events.
        
        Args:
            index: Index of the clicked tab
        """
        try:
            if 0 <= index < len(self.tabs):
                self._set_active_tab(index)
                
                # Emit tab changed signal
                tab_name = self.tabs_config[index]["name"]
                self.tab_changed.emit(tab_name)
                
                logger.debug(f"Tab clicked: {tab_name}")
            
        except Exception as e:
            logger.error(f"Failed to handle tab click: {e}")
    
    def _set_active_tab(self, index: int) -> None:
        """
        Set the active tab by index.
        
        Args:
            index: Index of the tab to activate
        """
        try:
            if 0 <= index < len(self.tabs):
                # Deactivate all tabs
                for tab in self.tabs:
                    tab.set_active(False)
                
                # Activate selected tab
                self.tabs[index].set_active(True)
                self.active_tab_index = index
                
                logger.debug(f"Active tab set to index: {index}")
            
        except Exception as e:
            logger.error(f"Failed to set active tab: {e}")
    
    def set_active_tab_by_name(self, tab_name: str) -> None:
        """
        Set the active tab by name.
        
        Args:
            tab_name: Name of the tab to activate
        """
        try:
            for i, tab_config in enumerate(self.tabs_config):
                if tab_config["name"] == tab_name:
                    self._set_active_tab(i)
                    return
            
            logger.warning(f"Tab not found: {tab_name}")
            
        except Exception as e:
            logger.error(f"Failed to set active tab by name: {e}")
    
    def get_active_tab_name(self) -> str:
        """
        Get the name of the currently active tab.
        
        Returns:
            str: Name of the active tab
        """
        try:
            if 0 <= self.active_tab_index < len(self.tabs_config):
                return self.tabs_config[self.active_tab_index]["name"]
            return ""
            
        except Exception as e:
            logger.error(f"Failed to get active tab name: {e}")
            return ""
    
    def keyPressEvent(self, event) -> None:
        """Handle keyboard navigation."""
        try:
            key = event.key()
            
            # Tab navigation with Ctrl+1-9
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                if Qt.Key.Key_1 <= key <= Qt.Key.Key_9:
                    tab_index = key - Qt.Key.Key_1
                    if tab_index < len(self.tabs):
                        self._on_tab_clicked(tab_index)
                        return
            
            # Arrow key navigation
            elif key == Qt.Key.Key_Left:
                new_index = (self.active_tab_index - 1) % len(self.tabs)
                self._on_tab_clicked(new_index)
                return
            elif key == Qt.Key.Key_Right:
                new_index = (self.active_tab_index + 1) % len(self.tabs)
                self._on_tab_clicked(new_index)
                return
            
            # Pass event to parent
            super().keyPressEvent(event)
            
        except Exception as e:
            logger.error(f"Failed to handle key press: {e}")
            super().keyPressEvent(event)
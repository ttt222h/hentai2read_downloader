"""
Enhanced Status Bar Component

Real-time status bar with progress indicators and system information.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import (
    QStatusBar, QLabel, QProgressBar, QPushButton,
    QHBoxLayout, QWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QColor, QPen

from loguru import logger


class SimpleStatusIndicator(QWidget):
    """Simple status indicator without complex animations."""
    
    STATUS_COLORS = {
        'idle': '#6C757D',      # Gray
        'queued': '#FFC107',    # Yellow
        'downloading': '#007BFF', # Blue
        'converting': '#17A2B8', # Cyan
        'completed': '#28A745',  # Green
        'error': '#DC3545',     # Red
        'paused': '#FD7E14'     # Orange
    }
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize status indicator."""
        super().__init__(parent)
        
        self.current_status = 'idle'
        self.setFixedSize(12, 12)
    
    def set_status(self, status: str) -> None:
        """Set the current status."""
        if status != self.current_status:
            self.current_status = status
            self.update()
    
    def paintEvent(self, event) -> None:
        """Paint the status indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get color for current status
        color = QColor(self.STATUS_COLORS.get(self.current_status, '#6C757D'))
        
        # Draw circle
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(120), 1))
        painter.drawEllipse(1, 1, 10, 10)


class EnhancedStatusBar(QStatusBar):
    """
    Enhanced status bar with real-time updates and progress tracking.
    
    Features:
    - Real-time download statistics
    - Progress indicator for active operations
    - System resource monitoring
    - Quick action buttons
    - Status history
    """
    
    # Signals
    show_progress_requested = pyqtSignal()
    show_logs_requested = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize enhanced status bar."""
        super().__init__(parent)
        
        # State tracking
        self.current_stats = {
            'active': 0,
            'queued': 0,
            'completed': 0,
            'failed': 0,
            'total_speed': 0.0
        }
        
        self.status_history = []
        self.max_history = 50
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system_info)
        self.update_timer.start(5000)  # Update every 5 seconds
        
        # Initial status
        self.show_ready_status()
        
        logger.debug("Enhanced status bar initialized")
    
    def _setup_ui(self) -> None:
        """Setup the status bar UI components."""
        # Main status label (permanent widget)
        self.status_label = QLabel("Ready")
        self.status_label.setMinimumWidth(200)
        self.addWidget(self.status_label)
        
        # Progress section (permanent widget)
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(5, 0, 5, 0)
        
        # Status indicator
        self.status_indicator = SimpleStatusIndicator()
        progress_layout.addWidget(self.status_indicator)
        
        # Mini progress bar
        self.mini_progress = QProgressBar()
        self.mini_progress.setMaximumWidth(100)
        self.mini_progress.setMaximumHeight(16)
        self.mini_progress.setVisible(False)
        progress_layout.addWidget(self.mini_progress)
        
        # Speed indicator
        self.speed_label = QLabel("")
        self.speed_label.setMinimumWidth(80)
        progress_layout.addWidget(self.speed_label)
        
        self.addPermanentWidget(progress_widget)
        
        # System info
        self.system_label = QLabel("")
        self.system_label.setMinimumWidth(100)
        self.addPermanentWidget(self.system_label)
    
    def _connect_signals(self) -> None:
        """Connect status bar signals."""
        pass  # No signals to connect for simplified version
    
    def update_download_stats(self, stats: Dict[str, Any]) -> None:
        """
        Update download statistics.
        
        Args:
            stats: Statistics dictionary
        """
        try:
            self.current_stats.update(stats)
            
            # Update main status
            if stats.get('active', 0) > 0:
                status_text = f"Downloading: {stats['active']} active"
                if stats.get('queued', 0) > 0:
                    status_text += f", {stats['queued']} queued"
                
                self.status_indicator.set_status("downloading")
                self.mini_progress.setVisible(True)
                
                # Calculate overall progress if possible
                total = stats.get('active', 0) + stats.get('queued', 0) + stats.get('completed', 0)
                if total > 0:
                    progress = int((stats.get('completed', 0) / total) * 100)
                    self.mini_progress.setValue(progress)
                
            elif stats.get('queued', 0) > 0:
                status_text = f"Queued: {stats['queued']} downloads"
                self.status_indicator.set_status("queued")
                self.mini_progress.setVisible(False)
                
            elif stats.get('failed', 0) > 0:
                status_text = f"Completed with {stats['failed']} errors"
                self.status_indicator.set_status("error")
                self.mini_progress.setVisible(False)
                
            else:
                status_text = "Ready"
                self.status_indicator.set_status("idle")
                self.mini_progress.setVisible(False)
            
            self.status_label.setText(status_text)
            
            # Update speed display
            if stats.get('total_speed', 0) > 0:
                speed_mb = stats['total_speed'] / (1024 * 1024)
                self.speed_label.setText(f"{speed_mb:.1f} MB/s")
            else:
                self.speed_label.setText("")
            
            # Add to history
            self._add_to_history(status_text)
            
        except Exception as e:
            logger.error(f"Failed to update download stats: {e}")
    
    def show_message(self, message: str, timeout: int = 3000) -> None:
        """
        Show a temporary message.
        
        Args:
            message: Message to display
            timeout: Timeout in milliseconds
        """
        super().showMessage(message, timeout)
        self._add_to_history(message)
    
    def show_ready_status(self) -> None:
        """Show ready status."""
        self.status_label.setText("Ready")
        self.status_indicator.set_status("idle")
        self.mini_progress.setVisible(False)
        self.speed_label.setText("")
    
    def show_error_status(self, error_message: str) -> None:
        """
        Show error status.
        
        Args:
            error_message: Error message to display
        """
        self.status_label.setText(f"Error: {error_message}")
        self.status_indicator.set_status("error")
        self.mini_progress.setVisible(False)
        self.speed_label.setText("")
        self._add_to_history(f"Error: {error_message}")
    
    def show_success_status(self, message: str) -> None:
        """
        Show success status.
        
        Args:
            message: Success message to display
        """
        self.status_label.setText(message)
        self.status_indicator.set_status("completed")
        self.mini_progress.setVisible(False)
        self._add_to_history(message)
        
        # Auto-clear after 5 seconds
        QTimer.singleShot(5000, self.show_ready_status)
    
    def _update_system_info(self) -> None:
        """Update system information display."""
        try:
            import psutil
            
            # Get memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Format system info
            system_info = f"CPU: {cpu_percent:.0f}% | RAM: {memory_percent:.0f}%"
            self.system_label.setText(system_info)
            
        except ImportError:
            # psutil not available, show basic info
            self.system_label.setText("System: OK")
        except Exception as e:
            logger.debug(f"Failed to update system info: {e}")
            self.system_label.setText("System: N/A")
    
    def _add_to_history(self, message: str) -> None:
        """
        Add message to status history.
        
        Args:
            message: Message to add
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        history_entry = f"[{timestamp}] {message}"
        
        self.status_history.append(history_entry)
        
        # Limit history size
        if len(self.status_history) > self.max_history:
            self.status_history.pop(0)
    
    def get_status_history(self) -> list:
        """
        Get status history.
        
        Returns:
            List of status history entries
        """
        return self.status_history.copy()
    
    def clear_history(self) -> None:
        """Clear status history."""
        self.status_history.clear()
    
    def set_progress_visible(self, visible: bool) -> None:
        """
        Set progress indicator visibility.
        
        Args:
            visible: Whether to show progress indicator
        """
        self.mini_progress.setVisible(visible)
    
    def set_progress_value(self, value: int) -> None:
        """
        Set progress value.
        
        Args:
            value: Progress value (0-100)
        """
        self.mini_progress.setValue(value)
        if value > 0:
            self.mini_progress.setVisible(True)
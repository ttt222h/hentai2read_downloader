"""
Error Handling Dialogs

Specialized dialogs for error reporting and handling.
"""

from typing import Optional, List, Dict, Any
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QFrame,
    QMessageBox, QCheckBox, QComboBox, QSpinBox,
    QDialogButtonBox, QTabWidget, QWidget, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap

from loguru import logger
from datetime import datetime


class ErrorDialog(QDialog):
    """
    Enhanced error dialog with detailed information and actions.
    """
    
    retry_requested = pyqtSignal()
    ignore_requested = pyqtSignal()
    
    def __init__(self, 
                 title: str,
                 message: str,
                 details: str = "",
                 error_type: str = "error",
                 parent: Optional[QWidget] = None):
        """
        Initialize error dialog.
        
        Args:
            title: Dialog title
            message: Main error message
            details: Detailed error information
            error_type: Type of error (error, warning, critical)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.error_type = error_type
        self.details = details
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(500, 400)
        
        self._setup_ui(message)
        self._connect_signals()
    
    def _setup_ui(self, message: str) -> None:
        """Setup the error dialog UI."""
        layout = QVBoxLayout(self)
        
        # Header with icon and message
        header_layout = QHBoxLayout()
        
        # Error icon
        icon_label = QLabel()
        icon_label.setFixedSize(48, 48)
        
        # Set icon based on error type
        if self.error_type == "critical":
            icon_label.setText("🚨")
        elif self.error_type == "warning":
            icon_label.setText("⚠️")
        else:
            icon_label.setText("❌")
        
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFont(QFont("Segoe UI", 24))
        
        # Message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(QFont("Segoe UI", 11))
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(message_label, 1)
        
        layout.addLayout(header_layout)
        
        # Details section (if provided)
        if self.details:
            details_frame = QFrame()
            details_frame.setObjectName("DetailsFrame")
            details_layout = QVBoxLayout(details_frame)
            
            details_label = QLabel("Error Details:")
            details_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            details_layout.addWidget(details_label)
            
            self.details_text = QTextEdit()
            self.details_text.setPlainText(self.details)
            self.details_text.setReadOnly(True)
            self.details_text.setMaximumHeight(150)
            self.details_text.setFont(QFont("Consolas", 9))
            details_layout.addWidget(self.details_text)
            
            layout.addWidget(details_frame)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # Copy to clipboard button
        self.copy_button = QPushButton("Copy Details")
        self.copy_button.setObjectName("secondary")
        
        # Report bug button
        self.report_button = QPushButton("Report Bug")
        self.report_button.setObjectName("secondary")
        
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.report_button)
        button_layout.addStretch()
        
        # Standard buttons
        if self.error_type != "critical":
            self.retry_button = QPushButton("Retry")
            self.retry_button.setObjectName("primary")
            button_layout.addWidget(self.retry_button)
            
            self.ignore_button = QPushButton("Ignore")
            self.ignore_button.setObjectName("secondary")
            button_layout.addWidget(self.ignore_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("primary")
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect dialog signals."""
        self.copy_button.clicked.connect(self._copy_to_clipboard)
        self.report_button.clicked.connect(self._report_bug)
        self.close_button.clicked.connect(self.reject)
        
        if hasattr(self, 'retry_button'):
            self.retry_button.clicked.connect(self._on_retry)
        
        if hasattr(self, 'ignore_button'):
            self.ignore_button.clicked.connect(self._on_ignore)
    
    def _copy_to_clipboard(self) -> None:
        """Copy error details to clipboard."""
        try:
            from PyQt6.QtGui import QGuiApplication
            
            clipboard_text = f"Error: {self.windowTitle()}\n"
            if self.details:
                clipboard_text += f"Details:\n{self.details}\n"
            clipboard_text += f"Timestamp: {datetime.now().isoformat()}"
            
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(clipboard_text)
            
            # Show confirmation
            QMessageBox.information(self, "Copied", "Error details copied to clipboard.")
            
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
    
    def _report_bug(self) -> None:
        """Open bug report dialog."""
        try:
            bug_dialog = BugReportDialog(self.windowTitle(), self.details, self)
            bug_dialog.exec()
        except Exception as e:
            logger.error(f"Failed to open bug report dialog: {e}")
    
    def _on_retry(self) -> None:
        """Handle retry button click."""
        self.retry_requested.emit()
        self.accept()
    
    def _on_ignore(self) -> None:
        """Handle ignore button click."""
        self.ignore_requested.emit()
        self.accept()


class BugReportDialog(QDialog):
    """
    Dialog for reporting bugs with error details.
    """
    
    def __init__(self, error_title: str, error_details: str, parent: Optional[QWidget] = None):
        """
        Initialize bug report dialog.
        
        Args:
            error_title: Title of the error
            error_details: Detailed error information
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.error_title = error_title
        self.error_details = error_details
        
        self.setWindowTitle("Report Bug")
        self.setModal(True)
        self.resize(600, 500)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the bug report dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🐛 Report a Bug")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Help us improve by reporting this error. Your feedback is valuable!")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Form fields
        form_frame = QFrame()
        form_layout = QVBoxLayout(form_frame)
        
        # Error summary (read-only)
        summary_label = QLabel("Error Summary:")
        summary_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        form_layout.addWidget(summary_label)
        
        self.summary_text = QTextEdit()
        self.summary_text.setPlainText(self.error_title)
        self.summary_text.setMaximumHeight(60)
        self.summary_text.setReadOnly(True)
        form_layout.addWidget(self.summary_text)
        
        # User description
        user_desc_label = QLabel("What were you doing when this error occurred?")
        user_desc_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        form_layout.addWidget(user_desc_label)
        
        self.user_desc_text = QTextEdit()
        self.user_desc_text.setPlaceholderText("Please describe the steps that led to this error...")
        self.user_desc_text.setMaximumHeight(100)
        form_layout.addWidget(self.user_desc_text)
        
        # Technical details (collapsible)
        tech_label = QLabel("Technical Details:")
        tech_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        form_layout.addWidget(tech_label)
        
        self.tech_details_text = QTextEdit()
        self.tech_details_text.setPlainText(self.error_details)
        self.tech_details_text.setReadOnly(True)
        self.tech_details_text.setMaximumHeight(150)
        self.tech_details_text.setFont(QFont("Consolas", 9))
        form_layout.addWidget(self.tech_details_text)
        
        # Options
        self.include_logs_cb = QCheckBox("Include application logs")
        self.include_logs_cb.setChecked(True)
        form_layout.addWidget(self.include_logs_cb)
        
        layout.addWidget(form_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("secondary")
        
        self.send_button = QPushButton("Send Report")
        self.send_button.setObjectName("primary")
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.send_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect dialog signals."""
        self.cancel_button.clicked.connect(self.reject)
        self.send_button.clicked.connect(self._send_report)
    
    def _send_report(self) -> None:
        """Send the bug report."""
        try:
            # In a real application, this would send the report to a server
            # For now, we'll just show a confirmation and save locally
            
            report_data = {
                'error_title': self.error_title,
                'error_details': self.error_details,
                'user_description': self.user_desc_text.toPlainText(),
                'include_logs': self.include_logs_cb.isChecked(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Save report locally (in a real app, send to server)
            self._save_report_locally(report_data)
            
            QMessageBox.information(
                self,
                "Report Sent",
                "Thank you for your bug report! We'll investigate this issue."
            )
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Failed to send bug report: {e}")
            QMessageBox.critical(self, "Error", f"Failed to send report: {e}")
    
    def _save_report_locally(self, report_data: Dict[str, Any]) -> None:
        """Save bug report locally."""
        try:
            import json
            from pathlib import Path
            
            reports_dir = Path("bug_reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = reports_dir / f"bug_report_{timestamp}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Bug report saved to {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save bug report locally: {e}")


class MultiErrorDialog(QDialog):
    """
    Dialog for displaying multiple errors at once.
    """
    
    def __init__(self, errors: List[Dict[str, str]], parent: Optional[QWidget] = None):
        """
        Initialize multi-error dialog.
        
        Args:
            errors: List of error dictionaries with 'title', 'message', 'details'
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.errors = errors
        
        self.setWindowTitle(f"Multiple Errors ({len(errors)})")
        self.setModal(True)
        self.resize(600, 400)
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the multi-error dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"⚠️ {len(self.errors)} Errors Occurred")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Error list
        self.error_list = QListWidget()
        
        for i, error in enumerate(self.errors):
            item = QListWidgetItem(f"{i+1}. {error.get('title', 'Unknown Error')}")
            item.setData(Qt.ItemDataRole.UserRole, error)
            self.error_list.addItem(item)
        
        layout.addWidget(self.error_list)
        
        # Details area
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        layout.addWidget(self.details_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setObjectName("secondary")
        
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("primary")
        
        button_layout.addStretch()
        button_layout.addWidget(self.clear_all_button)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self) -> None:
        """Connect dialog signals."""
        self.error_list.currentItemChanged.connect(self._on_error_selected)
        self.clear_all_button.clicked.connect(self._clear_all_errors)
        self.close_button.clicked.connect(self.accept)
    
    def _on_error_selected(self, current, previous) -> None:
        """Handle error selection."""
        if current:
            error_data = current.data(Qt.ItemDataRole.UserRole)
            details = f"Message: {error_data.get('message', 'N/A')}\n\n"
            details += f"Details: {error_data.get('details', 'N/A')}"
            self.details_text.setPlainText(details)
    
    def _clear_all_errors(self) -> None:
        """Clear all errors."""
        self.error_list.clear()
        self.details_text.clear()
        self.errors.clear()
        self.accept()
"""
Settings Tab Components

Individual tab widgets for different settings categories.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QCheckBox, QComboBox, QFrame,
    QSpinBox, QFileDialog, QGroupBox, QFormLayout,
    QScrollArea, QSlider, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from loguru import logger
from core.config import Settings
from .path_selector import DirectorySelector


class BaseSettingsTab(QWidget):
    """Base class for settings tabs."""
    
    setting_changed = pyqtSignal(str, object)  # setting_name, value
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """Initialize base settings tab."""
        super().__init__(parent)
        self.config = config
        self.widgets = {}  # Store widget references
    
    def load_settings(self, config: Settings) -> None:
        """Load settings into the tab widgets."""
        raise NotImplementedError
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings from the tab."""
        raise NotImplementedError


class GeneralSettingsTab(BaseSettingsTab):
    """General application settings tab."""
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """Initialize general settings tab."""
        super().__init__(config, parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the general settings UI."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        
        # Download Settings Group
        download_group = QGroupBox("📁 Download Settings")
        download_layout = QFormLayout(download_group)
        
        # Download directory
        self.widgets['download_dir'] = QLineEdit()
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_download_dir)
        
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.widgets['download_dir'])
        dir_layout.addWidget(browse_button)
        
        download_layout.addRow("Download Directory:", dir_layout)
        
        # Default format
        self.widgets['default_format'] = QComboBox()
        self.widgets['default_format'].addItems(["images", "cbz", "pdf"])
        download_layout.addRow("Default Format:", self.widgets['default_format'])
        
        # Auto conversion
        self.widgets['auto_convert'] = QCheckBox("Automatically convert after download")
        download_layout.addRow("", self.widgets['auto_convert'])
        
        # Delete images after conversion
        self.widgets['delete_images'] = QCheckBox("Delete original images after conversion")
        download_layout.addRow("", self.widgets['delete_images'])
        
        layout.addWidget(download_group)
        
        # File Management Group
        file_group = QGroupBox("📂 File Management")
        file_layout = QFormLayout(file_group)
        
        # Create subdirectories
        self.widgets['create_subdirs'] = QCheckBox("Create subdirectories for each manga")
        file_layout.addRow("", self.widgets['create_subdirs'])
        
        # Organize by date
        self.widgets['organize_by_date'] = QCheckBox("Organize downloads by date")
        file_layout.addRow("", self.widgets['organize_by_date'])
        
        layout.addWidget(file_group)
        
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Text inputs
        self.widgets['download_dir'].textChanged.connect(
            lambda text: self.setting_changed.emit('DOWNLOAD_DIR', Path(text))
        )
        
        # Combo boxes
        self.widgets['default_format'].currentTextChanged.connect(
            lambda text: self.setting_changed.emit('DEFAULT_FORMAT', text)
        )
        
        # Checkboxes
        for key in ['auto_convert', 'delete_images', 'create_subdirs', 'organize_by_date']:
            field_mapping = {
                'auto_convert': 'AUTO_CONVERT',
                'delete_images': 'DELETE_IMAGES_AFTER_CONVERSION',
                'create_subdirs': 'CREATE_SUBDIRS',
                'organize_by_date': 'ORGANIZE_BY_DATE'
            }
            self.widgets[key].toggled.connect(
                lambda checked, k=field_mapping[key]: self.setting_changed.emit(k, checked)
            )
    
    def _browse_download_dir(self) -> None:
        """Browse for download directory."""
        current_dir = self.widgets['download_dir'].text() or str(Path.home())
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            current_dir
        )
        
        if directory:
            self.widgets['download_dir'].setText(directory)
    
    def load_settings(self, config: Settings) -> None:
        """Load settings into widgets."""
        self.widgets['download_dir'].setText(str(config.DOWNLOAD_DIR))
        self.widgets['default_format'].setCurrentText(config.DEFAULT_FORMAT)
        self.widgets['auto_convert'].setChecked(config.AUTO_CONVERT)
        self.widgets['delete_images'].setChecked(config.DELETE_IMAGES_AFTER_CONVERSION)
        self.widgets['create_subdirs'].setChecked(config.CREATE_SUBDIRS)
        self.widgets['organize_by_date'].setChecked(config.ORGANIZE_BY_DATE)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return {
            'DOWNLOAD_DIR': Path(self.widgets['download_dir'].text()),
            'DEFAULT_FORMAT': self.widgets['default_format'].currentText(),
            'AUTO_CONVERT': self.widgets['auto_convert'].isChecked(),
            'DELETE_IMAGES_AFTER_CONVERSION': self.widgets['delete_images'].isChecked(),
            'CREATE_SUBDIRS': self.widgets['create_subdirs'].isChecked(),
            'ORGANIZE_BY_DATE': self.widgets['organize_by_date'].isChecked(),
        }


class PerformanceSettingsTab(BaseSettingsTab):
    """Performance and download settings tab."""
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """Initialize performance settings tab."""
        super().__init__(config, parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the performance settings UI."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        
        # Download Performance Group
        perf_group = QGroupBox("🚀 Download Performance")
        perf_layout = QFormLayout(perf_group)
        
        # Max concurrent downloads
        self.widgets['max_concurrent'] = QSpinBox()
        self.widgets['max_concurrent'].setRange(1, 16)
        self.widgets['max_concurrent'].setSuffix(" downloads")
        perf_layout.addRow("Max Concurrent Downloads:", self.widgets['max_concurrent'])
        
        # Max workers per download
        self.widgets['max_workers'] = QSpinBox()
        self.widgets['max_workers'].setRange(1, 32)
        self.widgets['max_workers'].setSuffix(" workers")
        perf_layout.addRow("Workers per Download:", self.widgets['max_workers'])
        
        # Connection timeout
        self.widgets['timeout'] = QSpinBox()
        self.widgets['timeout'].setRange(5, 120)
        self.widgets['timeout'].setSuffix(" seconds")
        perf_layout.addRow("Connection Timeout:", self.widgets['timeout'])
        
        # Retry attempts
        self.widgets['retry_attempts'] = QSpinBox()
        self.widgets['retry_attempts'].setRange(0, 10)
        self.widgets['retry_attempts'].setSuffix(" attempts")
        perf_layout.addRow("Retry Attempts:", self.widgets['retry_attempts'])
        
        layout.addWidget(perf_group)
        
        # Memory Management Group
        memory_group = QGroupBox("💾 Memory Management")
        memory_layout = QFormLayout(memory_group)
        
        # Image cache size
        self.widgets['cache_size'] = QSpinBox()
        self.widgets['cache_size'].setRange(10, 1000)
        self.widgets['cache_size'].setSuffix(" MB")
        memory_layout.addRow("Image Cache Size:", self.widgets['cache_size'])
        
        # Enable memory optimization
        self.widgets['memory_optimization'] = QCheckBox("Enable memory optimization")
        memory_layout.addRow("", self.widgets['memory_optimization'])
        
        layout.addWidget(memory_group)
        
        # Network Settings Group
        network_group = QGroupBox("🌐 Network Settings")
        network_layout = QFormLayout(network_group)
        
        # User agent
        self.widgets['user_agent'] = QLineEdit()
        network_layout.addRow("User Agent:", self.widgets['user_agent'])
        
        # Rate limiting
        self.widgets['rate_limit'] = QCheckBox("Enable rate limiting")
        network_layout.addRow("", self.widgets['rate_limit'])
        
        # Requests per second
        self.widgets['requests_per_sec'] = QSpinBox()
        self.widgets['requests_per_sec'].setRange(1, 20)
        self.widgets['requests_per_sec'].setSuffix(" req/sec")
        network_layout.addRow("Max Requests/Second:", self.widgets['requests_per_sec'])
        
        layout.addWidget(network_group)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Spin boxes
        spin_widgets = ['max_concurrent', 'max_workers', 'timeout', 'retry_attempts',
                       'cache_size', 'requests_per_sec']
        field_mapping = {
            'max_concurrent': 'MAX_CONCURRENT_DOWNLOADS',
            'max_workers': 'MAX_WORKERS',
            'timeout': 'TIMEOUT',
            'retry_attempts': 'RETRY_ATTEMPTS',
            'cache_size': 'CACHE_SIZE',
            'requests_per_sec': 'REQUESTS_PER_SEC'
        }
        for key in spin_widgets:
            self.widgets[key].valueChanged.connect(
                lambda value, k=field_mapping[key]: self.setting_changed.emit(k, value)
            )
        
        # Text inputs
        self.widgets['user_agent'].textChanged.connect(
            lambda text: self.setting_changed.emit('USER_AGENT', text)
        )
        
        # Checkboxes
        field_mapping = {
            'memory_optimization': 'MEMORY_OPTIMIZATION',
            'rate_limit': 'RATE_LIMIT'
        }
        for key in ['memory_optimization', 'rate_limit']:
            self.widgets[key].toggled.connect(
                lambda checked, k=field_mapping[key]: self.setting_changed.emit(k, checked)
            )
    
    def load_settings(self, config: Settings) -> None:
        """Load settings into widgets."""
        self.widgets['max_concurrent'].setValue(config.MAX_CONCURRENT_DOWNLOADS)
        self.widgets['max_workers'].setValue(config.MAX_WORKERS)
        self.widgets['timeout'].setValue(config.TIMEOUT)
        self.widgets['retry_attempts'].setValue(config.RETRY_ATTEMPTS)
        self.widgets['cache_size'].setValue(config.CACHE_SIZE)
        self.widgets['requests_per_sec'].setValue(config.REQUESTS_PER_SEC)
        self.widgets['user_agent'].setText(config.USER_AGENT)
        self.widgets['memory_optimization'].setChecked(config.MEMORY_OPTIMIZATION)
        self.widgets['rate_limit'].setChecked(config.RATE_LIMIT)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return {
            'MAX_CONCURRENT_DOWNLOADS': self.widgets['max_concurrent'].value(),
            'MAX_WORKERS': self.widgets['max_workers'].value(),
            'TIMEOUT': self.widgets['timeout'].value(),
            'RETRY_ATTEMPTS': self.widgets['retry_attempts'].value(),
            'CACHE_SIZE': self.widgets['cache_size'].value(),
            'MEMORY_OPTIMIZATION': self.widgets['memory_optimization'].isChecked(),
            'USER_AGENT': self.widgets['user_agent'].text(),
            'RATE_LIMIT': self.widgets['rate_limit'].isChecked(),
            'REQUESTS_PER_SEC': self.widgets['requests_per_sec'].value(),
        }


class AdvancedSettingsTab(BaseSettingsTab):
    """Advanced configuration settings tab."""
    
    def __init__(self, config: Settings, parent: Optional[QWidget] = None):
        """Initialize advanced settings tab."""
        super().__init__(config, parent)
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        """Setup the advanced settings UI."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(20)
        
        # Logging Group
        logging_group = QGroupBox("📝 Logging & Debug")
        logging_layout = QFormLayout(logging_group)
        
        # Log level
        self.widgets['log_level'] = QComboBox()
        self.widgets['log_level'].addItems(["DEBUG", "INFO", "WARNING", "ERROR", "NONE"])
        logging_layout.addRow("Log Level:", self.widgets['log_level'])
        
        # Enable file logging
        self.widgets['file_logging'] = QCheckBox("Save logs to file")
        logging_layout.addRow("", self.widgets['file_logging'])
        
        # Debug mode
        self.widgets['debug_mode'] = QCheckBox("Enable debug mode")
        logging_layout.addRow("", self.widgets['debug_mode'])
        
        layout.addWidget(logging_group)
        
        # Conversion Settings Group
        conversion_group = QGroupBox("🔄 Conversion Settings")
        conversion_layout = QFormLayout(conversion_group)
        
        # PDF quality
        self.widgets['pdf_quality'] = QComboBox()
        self.widgets['pdf_quality'].addItems(["Low", "Medium", "High", "Maximum"])
        conversion_layout.addRow("PDF Quality:", self.widgets['pdf_quality'])
        
        # Image compression
        self.widgets['image_compression'] = QSlider(Qt.Orientation.Horizontal)
        self.widgets['image_compression'].setRange(1, 100)
        self.widgets['image_compression'].setValue(85)
        
        compression_layout = QHBoxLayout()
        compression_layout.addWidget(self.widgets['image_compression'])
        compression_label = QLabel("85%")
        self.widgets['image_compression'].valueChanged.connect(
            lambda v: compression_label.setText(f"{v}%")
        )
        compression_layout.addWidget(compression_label)
        
        conversion_layout.addRow("Image Compression:", compression_layout)
        
        layout.addWidget(conversion_group)
        layout.addStretch()
        
        scroll.setWidget(content)
        
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)
    
    def _connect_signals(self) -> None:
        """Connect widget signals."""
        # Combo boxes
        field_mapping = {
            'log_level': 'LOG_LEVEL',
            'pdf_quality': 'PDF_QUALITY'
        }
        for key in ['log_level', 'pdf_quality']:
            self.widgets[key].currentTextChanged.connect(
                lambda text, k=field_mapping[key]: self.setting_changed.emit(k, text)
            )
        
        # Sliders
        self.widgets['image_compression'].valueChanged.connect(
            lambda value: self.setting_changed.emit('IMAGE_COMPRESSION', value)
        )
        
        # Checkboxes
        field_mapping = {
            'file_logging': 'FILE_LOGGING',
            'debug_mode': 'DEBUG_MODE'
        }
        checkbox_keys = ['file_logging', 'debug_mode']
        for key in checkbox_keys:
            self.widgets[key].toggled.connect(
                lambda checked, k=field_mapping[key]: self.setting_changed.emit(k, checked)
            )
    
    def load_settings(self, config: Settings) -> None:
        """Load settings into widgets."""
        self.widgets['log_level'].setCurrentText(config.LOG_LEVEL)
        self.widgets['pdf_quality'].setCurrentText(config.PDF_QUALITY)
        self.widgets['image_compression'].setValue(config.IMAGE_COMPRESSION)
        self.widgets['file_logging'].setChecked(config.FILE_LOGGING)
        self.widgets['debug_mode'].setChecked(config.DEBUG_MODE)
    
    def get_settings(self) -> Dict[str, Any]:
        """Get current settings."""
        return {
            'LOG_LEVEL': self.widgets['log_level'].currentText(),
            'FILE_LOGGING': self.widgets['file_logging'].isChecked(),
            'DEBUG_MODE': self.widgets['debug_mode'].isChecked(),
            'PDF_QUALITY': self.widgets['pdf_quality'].currentText(),
            'IMAGE_COMPRESSION': self.widgets['image_compression'].value(),
        }
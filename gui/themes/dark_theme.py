"""
Dark Theme Implementation

This module provides the dark glass morphism theme styling
for the GUI application using Qt stylesheets.
"""

from typing import Dict, Any


class DarkTheme:
    """
    Dark theme with glass morphism effects.
    
    Provides a modern, dark-themed interface with glass morphism
    styling, smooth animations, and premium visual effects.
    """
    
    # Color palette
    COLORS = {
        # Primary backgrounds
        'bg_primary': '#0D1117',
        'bg_secondary': '#161B22', 
        'bg_tertiary': '#21262D',
        
        # Accent colors
        'accent_primary': '#58A6FF',
        'accent_secondary': '#F78166',
        'accent_success': '#3FB950',
        'accent_warning': '#D29922',
        
        # Text colors
        'text_primary': '#F0F6FC',
        'text_secondary': '#8B949E',
        'text_muted': '#6E7681',
        
        # Glass effects
        'glass_bg': 'rgba(22, 27, 34, 0.8)',
        'glass_border': 'rgba(240, 246, 252, 0.1)',
        'glass_shadow': 'rgba(0, 0, 0, 0.3)',
        
        # Interactive states
        'hover_bg': 'rgba(88, 166, 255, 0.1)',
        'pressed_bg': 'rgba(88, 166, 255, 0.2)',
        'focus_border': '#58A6FF',
    }
    
    # Typography
    FONTS = {
        'primary': 'Inter, "Segoe UI", "SF Pro Display", Ubuntu, sans-serif',
        'monospace': '"JetBrains Mono", "Consolas", "Monaco", monospace',
        'size_small': '9px',
        'size_normal': '10px',
        'size_medium': '12px',
        'size_large': '14px',
        'size_xlarge': '16px',
    }
    
    # Spacing and sizing
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '12px',
        'lg': '16px',
        'xl': '24px',
        'xxl': '32px',
    }
    
    # Border radius
    RADIUS = {
        'small': '6px',
        'medium': '8px',
        'large': '12px',
        'xlarge': '16px',
    }
    
    def get_stylesheet(self) -> str:
        """
        Generate the complete Qt stylesheet for the dark theme.
        
        Returns:
            str: Complete Qt stylesheet
        """
        return f"""
        /* Global Application Styling */
        QApplication {{
            background-color: {self.COLORS['bg_primary']};
            color: {self.COLORS['text_primary']};
            font-family: {self.FONTS['primary']};
            font-size: {self.FONTS['size_normal']};
        }}
        
        /* Main Window */
        QMainWindow {{
            background-color: {self.COLORS['bg_primary']};
            border: none;
        }}
        
        /* Glass Morphism Cards */
        QFrame#GlassCard {{
            background-color: {self.COLORS['glass_bg']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['large']};
            padding: {self.SPACING['lg']};
        }}
        
        /* Group Boxes */
        QGroupBox {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['medium']};
            color: {self.COLORS['text_primary']};
            font-weight: 600;
            padding-top: {self.SPACING['lg']};
            margin-top: {self.SPACING['sm']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 {self.SPACING['sm']};
            background-color: {self.COLORS['bg_secondary']};
            color: {self.COLORS['text_primary']};
            font-weight: 600;
        }}
        
        /* Modern Buttons */
        QPushButton {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            font-weight: 500;
            padding: {self.SPACING['sm']} {self.SPACING['md']};
            min-height: 32px;
        }}
        
        QPushButton:hover {{
            background-color: {self.COLORS['hover_bg']};
            border-color: {self.COLORS['accent_primary']};
        }}
        
        QPushButton:pressed {{
            background-color: {self.COLORS['pressed_bg']};
        }}
        
        QPushButton:disabled {{
            background-color: {self.COLORS['bg_secondary']};
            color: {self.COLORS['text_muted']};
            border-color: {self.COLORS['text_muted']};
        }}
        
        /* Primary Button Variant */
        QPushButton.primary {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.COLORS['accent_primary']},
                stop:1 #1F6FEB);
            border: none;
            color: white;
            font-weight: 600;
        }}
        
        QPushButton.primary:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #6CB6FF,
                stop:1 {self.COLORS['accent_primary']});
        }}
        
        /* Success Button Variant */
        QPushButton.success {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.COLORS['accent_success']},
                stop:1 #2EA043);
            border: none;
            color: white;
            font-weight: 600;
        }}
        
        /* Danger Button Variant */
        QPushButton.danger {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {self.COLORS['accent_secondary']},
                stop:1 #DA3633);
            border: none;
            color: white;
            font-weight: 600;
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['sm']};
            font-size: {self.FONTS['size_normal']};
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {self.COLORS['focus_border']};
            background-color: {self.COLORS['bg_tertiary']};
        }}
        
        QLineEdit::placeholder, QTextEdit::placeholder {{
            color: {self.COLORS['text_muted']};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['sm']};
            min-height: 24px;
        }}
        
        QComboBox:hover {{
            border-color: {self.COLORS['accent_primary']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {self.COLORS['text_secondary']};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            selection-background-color: {self.COLORS['accent_primary']};
        }}
        
        /* Progress Bars */
        QProgressBar {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            text-align: center;
            color: {self.COLORS['text_primary']};
            font-weight: 500;
            height: 20px;
        }}
        
        QProgressBar::chunk {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {self.COLORS['accent_primary']},
                stop:1 #1F6FEB);
            border-radius: {self.RADIUS['small']};
        }}
        
        /* Scrollbars */
        QScrollBar:vertical {{
            background-color: {self.COLORS['bg_secondary']};
            width: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.COLORS['text_muted']};
            border-radius: 6px;
            min-height: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.COLORS['text_secondary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.COLORS['bg_secondary']};
            height: 12px;
            border-radius: 6px;
            margin: 0;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.COLORS['text_muted']};
            border-radius: 6px;
            min-width: 20px;
            margin: 2px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.COLORS['text_secondary']};
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['large']};
            margin-top: -1px;
        }}
        
        QTabBar::tab {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-bottom: none;
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_secondary']};
            padding: {self.SPACING['sm']} {self.SPACING['lg']};
            margin-right: 2px;
            min-width: 80px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.COLORS['accent_primary']};
            color: white;
            font-weight: 600;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {self.COLORS['hover_bg']};
            color: {self.COLORS['text_primary']};
        }}
        
        /* Labels */
        QLabel {{
            color: {self.COLORS['text_primary']};
            background: transparent;
        }}
        
        QLabel.secondary {{
            color: {self.COLORS['text_secondary']};
        }}
        
        QLabel.muted {{
            color: {self.COLORS['text_muted']};
        }}
        
        QLabel.title {{
            font-size: {self.FONTS['size_large']};
            font-weight: 600;
            color: {self.COLORS['text_primary']};
        }}
        
        QLabel.subtitle {{
            font-size: {self.FONTS['size_medium']};
            font-weight: 500;
            color: {self.COLORS['text_secondary']};
        }}
        
        /* Checkboxes */
        QCheckBox {{
            color: {self.COLORS['text_primary']};
            spacing: {self.SPACING['sm']};
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: 3px;
            background-color: {self.COLORS['bg_secondary']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.COLORS['accent_primary']};
            border-color: {self.COLORS['accent_primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {self.COLORS['accent_primary']};
        }}
        
        /* Radio Buttons */
        QRadioButton {{
            color: {self.COLORS['text_primary']};
            spacing: {self.SPACING['sm']};
        }}
        
        QRadioButton::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: 8px;
            background-color: {self.COLORS['bg_secondary']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {self.COLORS['accent_primary']};
            border-color: {self.COLORS['accent_primary']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {self.COLORS['bg_secondary']};
            border-top: 1px solid {self.COLORS['glass_border']};
            color: {self.COLORS['text_secondary']};
            font-size: {self.FONTS['size_small']};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {self.COLORS['bg_primary']};
            border-bottom: 1px solid {self.COLORS['glass_border']};
            color: {self.COLORS['text_primary']};
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: {self.SPACING['sm']} {self.SPACING['md']};
        }}
        
        QMenuBar::item:selected {{
            background-color: {self.COLORS['hover_bg']};
            border-radius: {self.RADIUS['small']};
        }}
        
        /* Context Menus */
        QMenu {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['medium']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['xs']};
        }}
        
        QMenu::item {{
            padding: {self.SPACING['sm']} {self.SPACING['lg']};
            border-radius: {self.RADIUS['small']};
        }}
        
        QMenu::item:selected {{
            background-color: {self.COLORS['accent_primary']};
            color: white;
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['sm']};
            font-size: {self.FONTS['size_small']};
        }}
        
        /* Spin Boxes */
        QSpinBox, QDoubleSpinBox {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['small']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['sm']};
            min-height: 24px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {self.COLORS['focus_border']};
            background-color: {self.COLORS['bg_tertiary']};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: 3px;
            width: 16px;
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: 3px;
            width: 16px;
        }}
        
        /* List Widgets */
        QListWidget {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['medium']};
            color: {self.COLORS['text_primary']};
            alternate-background-color: {self.COLORS['bg_tertiary']};
        }}
        
        QListWidget::item {{
            padding: {self.SPACING['sm']};
            border-bottom: 1px solid {self.COLORS['glass_border']};
        }}
        
        QListWidget::item:selected {{
            background-color: {self.COLORS['accent_primary']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {self.COLORS['hover_bg']};
        }}
        
        /* Table Widgets */
        QTableWidget {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            border-radius: {self.RADIUS['medium']};
            color: {self.COLORS['text_primary']};
            gridline-color: {self.COLORS['glass_border']};
            alternate-background-color: {self.COLORS['bg_tertiary']};
        }}
        
        QTableWidget::item {{
            padding: {self.SPACING['sm']};
            border: none;
        }}
        
        QTableWidget::item:selected {{
            background-color: {self.COLORS['accent_primary']};
            color: white;
        }}
        
        QHeaderView::section {{
            background-color: {self.COLORS['bg_tertiary']};
            border: 1px solid {self.COLORS['glass_border']};
            color: {self.COLORS['text_primary']};
            padding: {self.SPACING['sm']};
            font-weight: 600;
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            background-color: {self.COLORS['bg_secondary']};
            border: 1px solid {self.COLORS['glass_border']};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {self.COLORS['accent_primary']};
            border: 2px solid {self.COLORS['accent_primary']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: #6CB6FF;
            border-color: #6CB6FF;
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollArea > QWidget > QWidget {{
            background-color: transparent;
        }}
        
        /* Frames */
        QFrame {{
            background-color: transparent;
            border: none;
        }}
        
        /* Splitters */
        QSplitter::handle {{
            background-color: {self.COLORS['glass_border']};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* Message Boxes */
        QMessageBox {{
            background-color: {self.COLORS['bg_secondary']};
            color: {self.COLORS['text_primary']};
        }}
        
        QMessageBox QLabel {{
            color: {self.COLORS['text_primary']};
        }}
        
        /* File Dialogs */
        QFileDialog {{
            background-color: {self.COLORS['bg_secondary']};
            color: {self.COLORS['text_primary']};
        }}
        
        /* Form Layout specific styling */
        QFormLayout QLabel {{
            color: {self.COLORS['text_primary']};
            font-weight: 500;
        }}
        """
    
    def get_colors(self) -> Dict[str, str]:
        """Get the theme color palette."""
        return self.COLORS.copy()
    
    def get_fonts(self) -> Dict[str, str]:
        """Get the theme font definitions."""
        return self.FONTS.copy()
    
    def get_spacing(self) -> Dict[str, str]:
        """Get the theme spacing values."""
        return self.SPACING.copy()
    
    def get_radius(self) -> Dict[str, str]:
        """Get the theme border radius values."""
        return self.RADIUS.copy()
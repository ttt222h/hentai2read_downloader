"""
GUI Widgets Module

This module contains all the custom widgets used in the
Hentai2Read Downloader GUI interface.
"""

from .navigation_bar import NavigationBar
from .download_widget import DownloadWidget
from .settings_widget import SettingsWidget
from .search_widget import SearchWidget

__all__ = [
    "NavigationBar",
    "DownloadWidget", 
    "SettingsWidget",
    "SearchWidget"
]
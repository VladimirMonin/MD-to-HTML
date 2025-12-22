"""
GUI пакет для MD-to-HTML конвертера.
Графический интерфейс на PyQt6.
"""

from .main_window import MainWindow
from .config_manager import ConfigManager
from .widgets import DropZone, InputDropZone

__all__ = ["MainWindow", "ConfigManager", "DropZone", "InputDropZone"]

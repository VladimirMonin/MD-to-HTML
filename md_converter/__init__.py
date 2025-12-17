"""MD-to-HTML Converter - модульный конвертер Markdown в HTML/EPUB."""

from .config import ConverterConfig
from .converter import Converter

__version__ = "2.0.0"
__all__ = ["Converter", "ConverterConfig"]

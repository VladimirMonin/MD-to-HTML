"""Постпроцессоры для финальной обработки HTML."""

from .mermaid_postprocessor import MermaidFixPostprocessor
from .plyr_wrap import PlyrWrapPostprocessor

__all__ = ["MermaidFixPostprocessor", "PlyrWrapPostprocessor"]

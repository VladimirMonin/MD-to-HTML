"""Базовый класс для препроцессоров Markdown."""

from abc import ABC, abstractmethod


class Preprocessor(ABC):
    """Базовый абстрактный класс для препроцессоров."""

    @abstractmethod
    def process(self, content: str) -> str:
        """
        Обработать содержимое Markdown.

        Args:
            content: Исходный Markdown текст

        Returns:
            Обработанный Markdown текст
        """
        pass

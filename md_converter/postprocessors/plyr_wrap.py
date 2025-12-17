"""Постпроцессор для обертывания audio/video в Plyr."""

import re


class PlyrWrapPostprocessor:
    """Оборачивает <audio> и <video> теги в Plyr-совместимую структуру."""

    def process(self, html: str) -> str:
        """Обработка audio/video тегов."""
        # TODO: Реализовать обертывание в Plyr
        # Для начала просто пропускаем
        return html

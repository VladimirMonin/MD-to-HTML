"""Постпроцессор для обертывания audio/video в красивые figure с Plyr."""

import re


class PlyrWrapPostprocessor:
    """Оборачивает <audio> и <video> теги в красивые figure с классами для Plyr."""

    def process(self, html: str) -> str:
        """Обработка audio/video тегов - добавление классов для Plyr и стилизации."""

        # ШАГ 1: Добавляем class="plyr-audio" к <audio> тегам (если ещё нет)
        html = re.sub(
            r"<audio(?![^>]*class=)([^>]*)>", r'<audio class="plyr-audio"\1>', html
        )

        # ШАГ 2: Добавляем class="plyr-video" к <video> тегам (если ещё нет)
        html = re.sub(
            r"<video(?![^>]*class=)([^>]*)>", r'<video class="plyr-video"\1>', html
        )

        # ШАГ 3: Добавляем классы к <figure> содержащим <audio>
        # Паттерн матчит <figure> без класса, за которым идёт audio
        html = re.sub(
            r"<figure>(\s*<audio)", r'<figure class="media-player media-audio">\1', html
        )

        # ШАГ 4: Добавляем классы к <figure> содержащим <video>
        html = re.sub(
            r"<figure>(\s*<video)", r'<figure class="media-player media-video">\1', html
        )

        # ШАГ 5: Обработка figure с Plyr-обёрнутыми элементами (когда Plyr уже добавил div.plyr)
        html = re.sub(
            r'<figure>(\s*<div class="plyr[^"]*plyr--audio)',
            r'<figure class="media-player media-audio">\1',
            html,
        )

        html = re.sub(
            r'<figure>(\s*<div class="plyr[^"]*plyr--video)',
            r'<figure class="media-player media-video">\1',
            html,
        )

        return html

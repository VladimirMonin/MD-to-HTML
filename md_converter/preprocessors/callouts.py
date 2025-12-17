"""Препроцессор для Obsidian Callouts → Pandoc Admonitions."""

import re
from .base import Preprocessor


class CalloutsPreprocessor(Preprocessor):
    """
    Преобразует Obsidian Callouts в Pandoc Divs.

    Поддерживаемые типы (Obsidian standard):
    - note, abstract/summary/tldr, info, todo, tip/hint/important
    - success/check/done, question/help/faq, warning/caution/attention
    - failure/fail/missing, danger/error, bug, example, quote/cite

    Синтаксис:
    > [!NOTE] Title  → ::: note
    > Content         Title
    >                  Content
                       :::
    """

    # Все поддерживаемые типы Obsidian callouts
    CALLOUT_TYPES = [
        "note",
        "abstract",
        "summary",
        "tldr",
        "info",
        "todo",
        "tip",
        "hint",
        "important",
        "success",
        "check",
        "done",
        "question",
        "help",
        "faq",
        "warning",
        "caution",
        "attention",
        "failure",
        "fail",
        "missing",
        "danger",
        "error",
        "bug",
        "example",
        "quote",
        "cite",
    ]

    def process(self, content: str) -> str:
        """Преобразование callouts в Pandoc divs."""
        lines = content.split("\n")
        result = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Проверяем начало callout: > [!TYPE] Title
            match = re.match(r"^>\s*\[!([a-zA-Z-]+)\]\s*(.*)", line)
            if match:
                callout_type = match.group(1).lower()
                title = match.group(2).strip()

                # Если тип не поддерживается, используем 'note'
                if callout_type not in self.CALLOUT_TYPES:
                    callout_type = "note"

                # Начало div блока
                result.append(f"\n::: {callout_type}")
                if title:
                    result.append(f"**{title}**\n")

                # Собираем содержимое (все строки начинающиеся с >)
                i += 1
                content_lines = []
                while i < len(lines) and lines[i].startswith(">"):
                    # Убираем > и пробел
                    clean_line = re.sub(r"^>\s?", "", lines[i])
                    content_lines.append(clean_line)
                    i += 1

                # Добавляем содержимое
                result.extend(content_lines)

                # Закрываем div
                result.append(":::")
                result.append("")  # Пустая строка после блока
                continue

            result.append(line)
            i += 1

        return "\n".join(result)

"""Препроцессор для Obsidian Callouts → stable Pandoc callout DOM."""

import html
import re
from .base import Preprocessor


class CalloutsPreprocessor(Preprocessor):
    """
    Преобразует Obsidian Callouts в Pandoc Divs со стабильным DOM-контрактом.

    Поддерживаемые типы (Obsidian standard):
    - note, abstract/summary/tldr, info, todo, tip/hint/important
    - success/check/done, question/help/faq, warning/caution/attention
    - failure/fail/missing, danger/error, bug, example, quote/cite

    Синтаксис:
    > [!NOTE] Title  → ::: {.callout .callout-note .note data-callout="note"}
    > Content            ::: {.callout-title}
    >                    <span class="callout-icon" aria-hidden="true"></span>
    >                    <span class="callout-title-text">Title</span>
    >                    :::
    >                    ::: {.callout-body}
    >                    Content
    >                    :::
    >                    :::
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

            # Проверяем начало callout: > [!TYPE] Title или > [!TYPE]
            match = re.match(r"^>\s*\[!([a-zA-Z-]+)\]\s*(.*)", line)
            if match:
                callout_type = match.group(1).lower()
                title = match.group(2).strip()

                # Если тип не поддерживается, используем 'note'
                if callout_type not in self.CALLOUT_TYPES:
                    callout_type = "note"

                display_title = title or callout_type.capitalize()

                # Начало div блока. Сохраняем старый type-class (note/warning/...)
                # для существующих CSS-переменных и добавляем стабильный contract.
                result.append(
                    f'\n::: {{.callout .callout-{callout_type} .{callout_type} data-callout="{callout_type}"}}'
                )

                # Собираем содержимое (все строки начинающиеся с >)
                i += 1
                content_lines = []
                first_line = True

                while i < len(lines) and lines[i].startswith(">"):
                    # Убираем > и пробел
                    clean_line = re.sub(r"^>\s?", "", lines[i])

                    # Если заголовок не был на первой строке, проверяем первую строку контента
                    if first_line and not title and clean_line.strip():
                        # Проверяем, это **Bold** заголовок?
                        bold_match = re.match(r"^\*\*(.+)\*\*\s*$", clean_line.strip())
                        if bold_match:
                            # Это заголовок, используем его
                            title = bold_match.group(1)
                            display_title = title
                            first_line = False
                            i += 1
                            continue

                    first_line = False
                    content_lines.append(clean_line)
                    i += 1

                # Заголовок contract-нодой. Текст экранируем, тело ниже оставляем
                # Markdown-ом, чтобы Pandoc продолжал рендерить списки/bold/code.
                result.append("::: {.callout-title}")
                result.append('<span class="callout-icon" aria-hidden="true"></span>')
                result.append(
                    f'<span class="callout-title-text">{html.escape(display_title)}</span>'
                )
                result.append(":::")
                result.append("")

                result.append("::: {.callout-body}")

                # Добавляем содержимое
                result.extend(content_lines)

                result.append(":::")

                # Закрываем div
                result.append(":::")
                result.append("")  # Пустая строка после блока
                continue

            result.append(line)
            i += 1

        return "\n".join(result)

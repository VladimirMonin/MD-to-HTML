"""Препроцессор для Mermaid диаграмм."""

import re
from .base import Preprocessor


class MermaidPreprocessor(Preprocessor):
    """
    Преобразует Mermaid блоки для HTML:
    ```mermaid → <pre class="mermaid">
    Для EPUB оставляет как есть (обработает mermaid-filter).

    Также автоматически добавляет кавычки к тексту узлов с Unicode
    (кириллица, эмодзи) и специальными символами (@) для совместимости
    с Mermaid v11+.
    """

    def __init__(self, format_type: str = "html"):
        """
        Args:
            format_type: "html" или "epub"
        """
        self.format_type = format_type

    def _fix_node_quotes(self, diagram_code: str) -> str:
        """
        Добавляет кавычки к тексту узлов, содержащих Unicode или @.

        Mermaid v11+ требует кавычки для:
        - Unicode символов (кириллица, эмодзи)
        - Символа @ (конфликтует с новым синтаксисом форм)

        Паттерны узлов:
        - [text] → ["text"] (прямоугольник)
        - (text) → ("text") (скруглённый)
        - {text} → {"text"} (ромб)
        - ((text)) → (("text")) (круг)
        - [[text]] → [["text"]] (подпроцесс)
        """
        # Регулярка для поиска текста узлов без кавычек
        # Ищем: открывающая скобка + текст без кавычек + закрывающая скобка
        # НЕ обрабатываем уже закавыченный текст

        # Паттерн для текста, который нужно закавычить:
        # - содержит не-ASCII символы (Unicode/кириллица)
        # - ИЛИ содержит @
        unicode_pattern = r"[^\x00-\x7F@]|@"

        def needs_quotes(text: str) -> bool:
            """Проверяет, нужны ли кавычки для текста."""
            # Уже в кавычках
            if text.startswith('"') and text.endswith('"'):
                return False
            if text.startswith("'") and text.endswith("'"):
                return False
            # Содержит Unicode или @
            return bool(re.search(unicode_pattern, text))

        def quote_if_needed(text: str) -> str:
            """Добавляет кавычки если нужно."""
            if needs_quotes(text):
                # Экранируем внутренние кавычки
                escaped = text.replace('"', '\\"')
                return f'"{escaped}"'
            return text

        # Паттерны для разных типов узлов
        # Формат: ID[text], ID(text), ID{text}, ID((text)), ID[[text]]
        # Также ID[text]:::class

        # Обрабатываем каждый тип скобок отдельно
        patterns = [
            # [text] - прямоугольник (не [[...]] и не ["..."])
            (r'(\w+)\[([^\[\]"]+)\]', r"[", r"]"),
            # (text) - скруглённый (не ((...)) и не ("..."))
            (r'(\w+)\(([^()"]+)\)(?!\))', r"(", r")"),
            # {text} - ромб (не {"..."})
            (r'(\w+)\{([^{}"]+)\}', r"{", r"}"),
            # ((text)) - круг
            (r'(\w+)\(\(([^()"]+)\)\)', r"((", r"))"),
            # [[text]] - подпроцесс
            (r'(\w+)\[\[([^\[\]"]+)\]\]', r"[[", r"]]"),
        ]

        result = diagram_code

        for pattern, open_br, close_br in patterns:

            def replacer(m):
                node_id = m.group(1)
                text = m.group(2)
                quoted_text = quote_if_needed(text)
                return f"{node_id}{open_br}{quoted_text}{close_br}"

            result = re.sub(pattern, replacer, result)

        return result

    def process(self, content: str) -> str:
        """Обработка Mermaid блоков."""
        if self.format_type != "html":
            return content

        def replace_mermaid(match):
            diagram_code = match.group(1)
            # Фиксим кавычки для Unicode текста
            diagram_code = self._fix_node_quotes(diagram_code)
            # Используем raw HTML block, чтобы Pandoc передал содержимое as-is
            # Формат ```{=html} говорит Pandoc не обрабатывать содержимое
            return (
                f'\n```{{=html}}\n<div class="mermaid">\n{diagram_code}\n</div>\n```\n'
            )

        content = re.sub(
            r"```mermaid\n(.*?)\n```", replace_mermaid, content, flags=re.DOTALL
        )
        return content

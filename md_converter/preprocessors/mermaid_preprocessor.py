"""Препроцессор для Mermaid диаграмм."""

import re
from .base import Preprocessor


class MermaidQuoteError(Exception):
    """Ошибка при обработке кавычек в Mermaid диаграмме."""

    def __init__(self, message: str, diagram_preview: str, problematic_node: str):
        self.diagram_preview = diagram_preview
        self.problematic_node = problematic_node
        super().__init__(
            f"{message}\n"
            f"Проблемный узел: {problematic_node}\n"
            f"Начало диаграммы:\n{diagram_preview}"
        )


class MermaidPreprocessor(Preprocessor):
    """
    Преобразует Mermaid блоки для HTML:
    ```mermaid → <pre class="mermaid">
    Для EPUB оставляет как есть (обработает mermaid-filter).

    Стратегия обработки кавычек:
    1. Узел ЗАКАВЫЧЕН ["текст"] → не трогаем
    2. Узел НЕ ЗАКАВЫЧЕН [текст] с Unicode/@ → добавляем кавычки
    3. Проблемный случай → выбрасываем понятную ошибку
    """

    # Паттерн для символов, требующих кавычки в Mermaid v11+
    NEEDS_QUOTES_PATTERN = re.compile(r"[^\x00-\x7F]|@")

    # Типы узлов: (open_bracket, close_bracket, name, is_double)
    # is_double = True для [[ ]], (( )) и [( )]
    NODE_TYPES = [
        ("[[", "]]", "подпроцесс", True),
        ("[(", ")]", "база данных", True),
        ("((", "))", "круг", True),
        ("{", "}", "ромб", False),
        ("[", "]", "прямоугольник", False),
        ("(", ")", "скруглённый", False),
    ]

    def __init__(self, format_type: str = "html"):
        """
        Args:
            format_type: "html" или "epub"
        """
        self.format_type = format_type
        self._current_diagram = ""  # Для сообщений об ошибках

    def _get_diagram_preview(self, diagram: str, lines: int = 5) -> str:
        """Возвращает первые N строк диаграммы для сообщения об ошибке."""
        diagram_lines = diagram.strip().split("\n")[:lines]
        return "\n".join(diagram_lines)

    def _is_quoted(self, content: str) -> bool:
        """Проверяет, закавычен ли контент."""
        content = content.strip()
        return (content.startswith('"') and content.endswith('"')) or (
            content.startswith("'") and content.endswith("'")
        )

    def _needs_quotes(self, content: str) -> bool:
        """Проверяет, нужны ли кавычки (есть Unicode или @)."""
        return bool(self.NEEDS_QUOTES_PATTERN.search(content))

    def _has_unbalanced_quotes(self, content: str) -> bool:
        """Проверяет, есть ли незакрытые кавычки внутри."""
        # Считаем кавычки (не экранированные)
        double_quotes = len(re.findall(r'(?<!\\)"', content))
        single_quotes = len(re.findall(r"(?<!\\)'", content))
        return (double_quotes % 2 != 0) or (single_quotes % 2 != 0)

    def _find_matching_bracket(
        self, text: str, start: int, open_br: str, close_br: str
    ) -> int:
        """
        Находит позицию закрывающей скобки, учитывая кавычки.

        Возвращает индекс символа ПОСЛЕ закрывающей скобки, или -1 если не найдено.
        """
        pos = start
        in_quotes = False
        quote_char = None

        while pos < len(text):
            char = text[pos]

            # Обработка кавычек
            if char in "\"'":
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char and (pos == 0 or text[pos - 1] != "\\"):
                    in_quotes = False
                    quote_char = None
                pos += 1
                continue

            # Внутри кавычек — пропускаем
            if in_quotes:
                pos += 1
                continue

            # Ищем закрывающую скобку
            if text[pos : pos + len(close_br)] == close_br:
                return pos + len(close_br)

            pos += 1

        return -1  # Не нашли

    def _process_node_match(
        self, node_id: str, content: str, open_br: str, close_br: str, node_type: str
    ) -> str:
        """
        Обрабатывает содержимое одного узла.

        Возвращает обработанный узел: ID + скобки + (возможно закавыченный) контент.
        """
        # === СЛУЧАЙ 1: Уже закавычен ===
        if self._is_quoted(content):
            return f"{node_id}{open_br}{content}{close_br}"

        # === СЛУЧАЙ 2: Не закавычен ===

        # Проверяем на проблемные ситуации
        if self._has_unbalanced_quotes(content):
            raise MermaidQuoteError(
                f"Незакрытая кавычка в узле типа '{node_type}'",
                self._get_diagram_preview(self._current_diagram),
                f"{node_id}{open_br}{content}{close_br}",
            )

        # Если есть Unicode/@ — нужно закавычить
        if self._needs_quotes(content):
            # Экранируем внутренние кавычки
            escaped = content.replace('"', '\\"')
            return f'{node_id}{open_br}"{escaped}"{close_br}'

        # === СЛУЧАЙ 3: ASCII без @ — оставляем как есть ===
        return f"{node_id}{open_br}{content}{close_br}"

    def _fix_node_quotes(self, diagram_code: str) -> str:
        """
        Обрабатывает кавычки во всех узлах диаграммы.

        Ключевая логика: ищем узлы вручную, учитывая кавычки,
        чтобы не обрабатывать содержимое внутри кавычек.

        ВАЖНО: Пропускаем содержимое внутри строковых литералов (в кавычках),
        чтобы не путать текст в note директивах с узлами диаграммы.
        """
        self._current_diagram = diagram_code
        result = []
        pos = 0
        in_quotes = False
        quote_char = None

        # Паттерн для ID узла (буква/подчёркивание + буквы/цифры/подчёркивания)
        id_pattern = re.compile(r"\b([A-Za-z_]\w*)")

        while pos < len(diagram_code):
            char = diagram_code[pos]

            # Обработка кавычек - пропускаем содержимое строковых литералов
            if char in "\"'":
                if not in_quotes:
                    # Входим в строковый литерал
                    in_quotes = True
                    quote_char = char
                    result.append(char)
                    pos += 1
                    continue
                elif char == quote_char and (pos == 0 or diagram_code[pos - 1] != "\\"):
                    # Выходим из строкового литерала
                    in_quotes = False
                    quote_char = None
                    result.append(char)
                    pos += 1
                    continue
                else:
                    # Другая кавычка внутри строки - просто добавляем
                    result.append(char)
                    pos += 1
                    continue

            # Если мы внутри кавычек - просто копируем символы
            if in_quotes:
                result.append(char)
                pos += 1
                continue

            # Вне кавычек - ищем ID узла
            match = id_pattern.match(diagram_code, pos)
            if not match:
                result.append(diagram_code[pos])
                pos += 1
                continue

            node_id = match.group(1)
            after_id = match.end()

            # Проверяем, какая скобка идёт после ID
            found_node = False
            for open_br, close_br, node_type, is_double in self.NODE_TYPES:
                if diagram_code[after_id : after_id + len(open_br)] == open_br:
                    # Нашли открывающую скобку
                    content_start = after_id + len(open_br)

                    # Ищем закрывающую скобку, учитывая кавычки
                    bracket_end = self._find_matching_bracket(
                        diagram_code, content_start, open_br, close_br
                    )

                    if bracket_end == -1:
                        # Не нашли закрывающую скобку — либо незакрытые кавычки,
                        # либо синтаксическая ошибка
                        # Извлекаем до конца строки для сообщения
                        line_end = diagram_code.find("\n", content_start)
                        if line_end == -1:
                            line_end = len(diagram_code)
                        problematic = diagram_code[pos:line_end]
                        raise MermaidQuoteError(
                            f"Не найдена закрывающая скобка '{close_br}' для узла типа '{node_type}'. "
                            f"Возможно, есть незакрытая кавычка.",
                            self._get_diagram_preview(self._current_diagram),
                            problematic,
                        )

                    # Извлекаем содержимое
                    content = diagram_code[content_start : bracket_end - len(close_br)]

                    # Обрабатываем узел
                    processed = self._process_node_match(
                        node_id, content, open_br, close_br, node_type
                    )
                    result.append(processed)
                    pos = bracket_end
                    found_node = True
                    break

            if not found_node:
                # Это просто слово, не узел — добавляем как есть
                result.append(node_id)
                pos = after_id

        return "".join(result)

    def _escape_quotes_in_strings(self, text: str) -> str:
        """
        Экранирует одинарные кавычки внутри строк в двойных кавычках.
        Для classDiagram note директив типа: note for X "Text with 'quotes'"
        Заменяет ' на временный маркер ___APOS___, который будет заменен на &#39;
        в постпроцессоре (после html.unescape).
        """
        result = []
        i = 0
        while i < len(text):
            if text[i] == '"':
                # Нашли начало строки в двойных кавычках
                result.append('"')
                i += 1
                # Ищем закрывающую кавычку
                while i < len(text) and text[i] != '"':
                    if text[i] == "'":
                        # Заменяем одинарную кавычку на временный маркер
                        result.append("___APOS___")
                    else:
                        result.append(text[i])
                    i += 1
                if i < len(text):
                    result.append('"')
                    i += 1
            else:
                result.append(text[i])
                i += 1
        return "".join(result)

    def process(self, content: str) -> str:
        """Обработка Mermaid блоков."""
        if self.format_type != "html":
            return content

        # Импортируем автоисправление
        from .mermaid_autofix import MermaidAutoFixPreprocessor

        autofix = MermaidAutoFixPreprocessor(format_type=self.format_type)

        # Сначала применяем автоисправление типичных ошибок AI
        content = autofix.process(content)

        def replace_mermaid(match):
            diagram_code = match.group(1)
            diagram_type = (
                diagram_code.strip().split()[0] if diagram_code.strip() else ""
            )

            # Для classDiagram экранируем одинарные кавычки внутри строк
            if diagram_type == "classDiagram":
                # Заменяем одинарные кавычки на #39; внутри двойных кавычек
                diagram_code = self._escape_quotes_in_strings(diagram_code)

            # _fix_node_quotes должен работать ТОЛЬКО для flowchart (graph)
            # Для sequenceDiagram, classDiagram, stateDiagram и т.д. НЕ применяем
            if diagram_type in ("graph", "flowchart"):
                # Фиксим кавычки для Unicode текста только в flowchart
                diagram_code = self._fix_node_quotes(diagram_code)

            # Используем raw HTML block, чтобы Pandoc передал содержимое as-is
            return (
                f'\n```{{=html}}\n<div class="mermaid">\n{diagram_code}\n</div>\n```\n'
            )

        content = re.sub(
            r"```mermaid\n(.*?)\n```", replace_mermaid, content, flags=re.DOTALL
        )
        return content

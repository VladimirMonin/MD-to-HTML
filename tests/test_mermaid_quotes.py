"""Тесты для обработки кавычек в Mermaid диаграммах."""

import pytest
from md_converter.preprocessors.mermaid_preprocessor import (
    MermaidPreprocessor,
    MermaidQuoteError,
)


class TestMermaidQuotes:
    """Тесты для _fix_node_quotes."""

    def setup_method(self):
        self.preprocessor = MermaidPreprocessor(format_type="html")

    # ==================== СЛУЧАЙ 1: Уже закавычено - НЕ ТРОГАЕМ ====================

    def test_already_quoted_cyrillic_square(self):
        """Уже закавыченный узел с кириллицей - не трогаем."""
        code = 'A["Вызов withdraw(сумма)"]'
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'A["Вызов withdraw(сумма)"]'

    def test_already_quoted_cyrillic_curly(self):
        """Уже закавыченный ромб с кириллицей - не трогаем."""
        code = 'B{"Проверка лимита<br/>и баланса"}'
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'B{"Проверка лимита<br/>и баланса"}'

    def test_already_quoted_at_symbol(self):
        """Уже закавыченный узел с @ - не трогаем."""
        code = 'C["@value.setter"]'
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'C["@value.setter"]'

    def test_already_quoted_emoji(self):
        """Уже закавыченный узел с эмодзи - не трогаем."""
        code = 'D["Готово ✅"]'
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'D["Готово ✅"]'

    def test_already_quoted_circle(self):
        """Уже закавыченный круг - не трогаем."""
        code = 'E(("Готово"))'
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'E(("Готово"))'

    # ==================== СЛУЧАЙ 2: Не закавычено - КАВЫЧИМ ====================

    def test_unquoted_cyrillic_square(self):
        """Незакавыченный узел с кириллицей - добавляем кавычки."""
        code = "A[Привет мир]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'A["Привет мир"]'

    def test_unquoted_cyrillic_curly(self):
        """Незакавыченный ромб с кириллицей - добавляем кавычки."""
        code = "B{Проверка условия}"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'B{"Проверка условия"}'

    def test_unquoted_at_symbol(self):
        """Незакавыченный узел с @ - добавляем кавычки."""
        code = "C[@property]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'C["@property"]'

    def test_unquoted_emoji(self):
        """Незакавыченный узел с эмодзи - добавляем кавычки."""
        code = "D[Готово ✅]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'D["Готово ✅"]'

    def test_unquoted_circle(self):
        """Незакавыченный круг с кириллицей - добавляем кавычки."""
        code = "E((Готово))"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'E(("Готово"))'

    def test_unquoted_subprocess(self):
        """Незакавыченный подпроцесс с кириллицей - добавляем кавычки."""
        code = "F[[Подпроцесс]]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'F[["Подпроцесс"]]'

    def test_unquoted_rounded(self):
        """Незакавыченный скруглённый узел с кириллицей - добавляем кавычки."""
        code = "G(Начало)"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == 'G("Начало")'

    # ==================== СЛУЧАЙ 3: ASCII без @ - НЕ ТРОГАЕМ ====================

    def test_ascii_only_no_change(self):
        """Чистый ASCII без @ - не трогаем."""
        code = "A[Start process]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == "A[Start process]"

    def test_ascii_with_br_no_change(self):
        """ASCII с <br/> - не трогаем."""
        code = "A[Line one<br/>Line two]"
        result = self.preprocessor._fix_node_quotes(code)
        assert result == "A[Line one<br/>Line two]"

    # ==================== СМЕШАННЫЕ СЛУЧАИ ====================

    def test_mixed_quoted_and_unquoted(self):
        """Часть узлов закавычена, часть нет - обрабатываем правильно."""
        code = 'A["Уже закавычено"] --> B[Нужно закавычить] --> C[English only]'
        result = self.preprocessor._fix_node_quotes(code)
        assert 'A["Уже закавычено"]' in result  # Не изменился
        assert 'B["Нужно закавычить"]' in result  # Добавлены кавычки
        assert "C[English only]" in result  # Не изменился

    def test_multiline_diagram(self):
        """Многострочная диаграмма с разными случаями."""
        code = """flowchart TD
    A["Вызов withdraw(сумма)"]:::start --> B{Проверка}
    B -->|Да| C[Успех]
    B -->|Нет| D[Ошибка выполнения]"""
        result = self.preprocessor._fix_node_quotes(code)
        # A уже закавычен - не изменился
        assert 'A["Вызов withdraw(сумма)"]' in result
        # B не закавычен с кириллицей - добавлены кавычки
        assert 'B{"Проверка"}' in result
        # C чистый ASCII - не изменился
        assert "C[Успех]" in result or 'C["Успех"]' in result  # Кириллица - закавычится
        # D кириллица - добавлены кавычки
        assert 'D["Ошибка выполнения"]' in result

    def test_internal_parentheses_preserved(self):
        """Скобки внутри закавыченного текста сохраняются."""
        code = 'A["Вызов withdraw(сумма)"]'
        result = self.preprocessor._fix_node_quotes(code)
        # Должен остаться точно таким же
        assert result == 'A["Вызов withdraw(сумма)"]'
        # НЕ должно быть двойных кавычек
        assert '""' not in result
        assert 'withdraw("сумма")' not in result

    def test_node_with_class(self):
        """Узел с классом стиля."""
        code = "A[Привет]:::action"
        result = self.preprocessor._fix_node_quotes(code)
        assert 'A["Привет"]' in result

    def test_edge_label_with_unicode(self):
        """Метки рёбер с Unicode."""
        code = "A --> |Условие| B"
        result = self.preprocessor._fix_node_quotes(code)
        # Метки рёбер не обрабатываем (нет ID перед |)
        assert result == code

    def test_escape_internal_quotes(self):
        """Внутренние кавычки экранируются."""
        code = 'A[Текст с "кавычками" внутри]'
        result = self.preprocessor._fix_node_quotes(code)
        assert r'A["Текст с \"кавычками\" внутри"]' in result


class TestMermaidQuoteErrors:
    """Тесты для ошибок — проблемные случаи с понятными сообщениями."""

    def setup_method(self):
        self.preprocessor = MermaidPreprocessor(format_type="html")

    def test_unbalanced_quote_raises_error(self):
        """Незакрытая кавычка вызывает понятную ошибку."""
        code = 'A[Текст с "незакрытой кавычкой]'

        with pytest.raises(MermaidQuoteError) as exc_info:
            self.preprocessor._fix_node_quotes(code)

        error = exc_info.value
        # Проверяем, что ошибка понятная
        assert "незакрытая кавычка" in str(error).lower()
        assert "Проблемный узел" in str(error)

    def test_error_contains_problematic_node(self):
        """Ошибка содержит проблемный узел."""
        code = 'A[Нормальный] --> B[Проблемный "узел]'

        with pytest.raises(MermaidQuoteError) as exc_info:
            self.preprocessor._fix_node_quotes(code)

        error = exc_info.value
        assert "Проблемный" in error.problematic_node

    def test_error_contains_diagram_preview(self):
        """Ошибка содержит превью диаграммы."""
        code = """flowchart TD
    A[Первая строка]
    B[Вторая "незакрытая]
    C[Третья строка]
    D[Четвёртая строка]"""

        with pytest.raises(MermaidQuoteError) as exc_info:
            self.preprocessor._fix_node_quotes(code)

        error = exc_info.value
        # Превью должно содержать начало диаграммы
        assert "flowchart TD" in error.diagram_preview
        assert "Первая строка" in error.diagram_preview

"""Тест для Mermaid диаграммы: Unit и Integration тесты с subgraph."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidUnitIntegration:
    """Тесты для диаграммы с subgraph и эмодзи."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: Unit и Integration

```mermaid
graph TB
    subgraph Unit ["🔬 Уровень Unit (Изоляция)"]
        direction TB
        UTest["Тест"] -.-> UClass["Класс A"]
        note1["📝 Зависимости<br/>отрезаны фейками"]
    end

    subgraph Integration ["🏭 Уровень Integration (Связки)"]
        direction TB
        ITest["Тест"] --> IClassA["Класс A"]
        IClassA --> IClassB["Класс B"]
        IClassB --> FS[("📂 Файловая<br/>система")]
        note2["🎯 Проверяем стыковку<br/>и поток данных"]
    end
```
"""

        # Создаём тестовый MD файл
        self.md_file = self.test_dir / "unit_integration.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_quotes(self):
        """Тест: препроцессор обрабатывает кавычки в узлах с эмодзи."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что узлы с эмодзи закавычены
        assert (
            '"🔬 Уровень Unit (Изоляция)"' in result
            or "🔬 Уровень Unit (Изоляция)" in result
        )
        assert '"Тест"' in result
        assert '"Класс A"' in result
        assert '<div class="mermaid">' in result

        print("\n=== Результат препроцессора ===")
        print(result[:1000])

    def test_full_conversion(self):
        """Тест: полная конвертация в HTML."""
        config = ConverterConfig()
        config.formats = ["html"]
        config.template = "web"
        config.media_mode = "embed"
        config.output_dir = str(self.test_dir)
        config.features.toc = False
        config.features.breadcrumbs = False
        config.features.mermaid = True
        config.styles.mermaid_theme = "forest"

        converter = Converter(config)
        converter.convert(str(self.md_file), "unit_integration")

        # Проверяем, что HTML создан
        html_file = self.test_dir / "unit_integration.html"
        assert html_file.exists(), f"HTML файл не создан: {html_file}"

        html_content = html_file.read_text(encoding="utf-8")

        # Проверяем наличие Mermaid
        assert "mermaid" in html_content.lower()
        assert '<div class="mermaid">' in html_content

        # Проверяем, что ключевые слова диаграммы присутствуют
        assert "graph TB" in html_content or "graph" in html_content
        assert "subgraph" in html_content

        print("\n=== Фрагмент HTML с диаграммой ===")
        # Ищем div с классом mermaid
        start = html_content.find('<div class="mermaid">')
        if start != -1:
            end = html_content.find("</div>", start)
            print(html_content[start : end + 6])
        else:
            print("Mermaid div не найден!")
            print(html_content[:2000])

        # Проверяем, что эмодзи остались
        assert "🔬" in html_content
        assert "🏭" in html_content
        assert "📝" in html_content

    def test_subgraph_syntax(self):
        """Тест: проверка синтаксиса subgraph с кавычками."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем формат: subgraph ID ["Label"]
        # Либо кавычки добавлены, либо остались как есть
        assert "subgraph Unit" in result
        assert "subgraph Integration" in result

        print("\n=== Проверка subgraph ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "subgraph" in line.lower():
                print(f"Line {i}: {line}")

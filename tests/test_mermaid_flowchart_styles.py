"""Тест для Mermaid flowchart с style директивами."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidFlowchartStyles:
    """Тесты для flowchart с style и stroke-dasharray."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: Flowchart со стилями

```mermaid
flowchart TD
    Main[("🚀 main.py<br/>(Точка входа)")]
    ConfigObj[("⚙️ Config Object<br/>(Экземпляр)")]
    
    subgraph Components ["Компоненты системы"]
        FP["📂 FileProcessor"]
        TG["✍️ TextGenerator"]
        IA["🖼️ ImageAnalyzer"]
        CC["⚙️ CourseCreator"]
    end

    Main -->|1. Загружает| ConfigObj
    ConfigObj -->|2. Передаётся в| FP
    ConfigObj -->|2. Передаётся в| TG
    ConfigObj -->|2. Передаётся в| IA
    ConfigObj -->|2. Передаётся в| CC

    style Main fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style ConfigObj fill:#ffd93d,stroke:#f4a261,stroke-width:2px,color:#000
    style Components fill:#e1f5fe,stroke:#01579b,stroke-dasharray: 5 5
```
"""

        self.md_file = self.test_dir / "flowchart_styles.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_handles_styles(self):
        """Тест: препроцессор не ломает style директивы."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что style директивы остались
        assert "style Main" in result
        assert "style ConfigObj" in result
        assert "style Components" in result
        assert "stroke-dasharray" in result

        print("\n=== Style директивы ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "style" in line.lower():
                print(f"Line {i}: {line}")

    def test_double_parentheses_nodes(self):
        """Тест: узлы с скобками [( )] - база данных."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем узлы БД: [(
        assert "[(" in result
        assert '")]' in result

        # Проверяем, что эмодзи в таких узлах закавычены
        print("\n=== Узлы базы данных ===")
        lines = result.split("\n")
        for line in lines:
            if "[(" in line:
                print(line.strip())

    def test_edge_labels_with_cyrillic(self):
        """Тест: метки рёбер с кириллицей."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Метки рёбер: -->|"текст"|
        assert "1. Загружает" in result
        assert "2. Передаётся в" in result

        print("\n=== Метки рёбер ===")
        lines = result.split("\n")
        for line in lines:
            if "-->" in line and "|" in line:
                print(line.strip())

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
        converter.convert(str(self.md_file), "flowchart_styles")

        html_file = self.test_dir / "flowchart_styles.html"
        assert html_file.exists()

        html_content = html_file.read_text(encoding="utf-8")

        # Проверяем наличие ключевых элементов
        assert "flowchart TD" in html_content or "flowchart" in html_content
        assert "style Main" in html_content
        assert "🚀" in html_content

        print("\n=== Фрагмент HTML ===")
        start = html_content.find('<div class="mermaid">')
        if start != -1:
            end = html_content.find("</div>", start)
            print(html_content[start : end + 6])

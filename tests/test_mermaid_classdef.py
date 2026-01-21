"""Тест для Mermaid с classDef и тройными двоеточиями."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidClassDef:
    """Тесты для flowchart с classDef и :::class применением."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: ClassDef и применение классов

```mermaid
flowchart TD
    classDef entry fill:#4ecdc4,stroke:#0a9396,color:#fff
    classDef config fill:#ffd93d,stroke:#f4a261,color:#000
    classDef logic fill:#e1f5fe,stroke:#01579b,color:#333
    classDef output fill:#ff6b6b,stroke:#c92a2a,color:#fff

    Start(("🚀 Запуск<br/>(main.py)")):::entry
    Config["⚙️ Загрузка Config<br/>(config.py)"]:::config
    Orchestrator["🤖 Инициализация CourseCreator<br/>(pipeline.py)"]:::logic
    
    subgraph Pipeline ["Внутри run_pipeline()"]
        direction TB
        Step1["📄 Чтение файла<br/>(FileProcessor)"]:::logic
        Step2["🖼️ Анализ изображений<br/>(ImageAnalyzer)"]:::logic
        Step3["✍️ Генерация текста<br/>(TextGenerator)"]:::logic
    end

    Result[("💾 Готовый файл<br/>(output/result.md)")]:::output

    Start --> Config
    Config --> Orchestrator
    Orchestrator --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Result

    Note["Файл main.py связывает<br/>конфигурацию и оркестратор"]
    Start -.- Note
    style Note fill:#fff5ad,stroke:#d4c46a,color:#333
```
"""

        self.md_file = self.test_dir / "classdef.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_classdef(self):
        """Тест: обработка classDef директив."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем все classDef
        assert "classDef entry" in result
        assert "classDef config" in result
        assert "classDef logic" in result
        assert "classDef output" in result

        print("\n=== ClassDef декларации ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "classDef" in line:
                print(f"Line {i}: {line}")

    def test_triple_colon_class_application(self):
        """Тест: применение классов через :::."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем применение классов
        assert ":::entry" in result
        assert ":::config" in result
        assert ":::logic" in result
        assert ":::output" in result

        print("\n=== Применение классов ::: ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if ":::" in line:
                print(f"Line {i}: {line}")

    def test_direction_in_subgraph(self):
        """Тест: direction TB внутри subgraph."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем direction
        assert "direction TB" in result

        print("\n=== Direction ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "direction" in line.lower():
                print(f"Line {i}: {line}")

    def test_dotted_edge_with_plain_node(self):
        """Тест: пунктирная связь -.- с обычным узлом."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем пунктирную связь
        assert "-.-" in result

        # Проверяем узел Note (без формы, просто текст)
        assert "Note[" in result or "note[" in result

        print("\n=== Пунктирные связи ===")
        lines = result.split("\n")
        for line in lines:
            if "-.-" in line:
                print(line.strip())

    def test_combined_style_and_classdef(self):
        """Тест: style и classDef используются вместе."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что оба механизма стилизации присутствуют
        assert "classDef" in result
        assert "style Note" in result

        print("\n=== Style и ClassDef вместе ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "style" in line.lower() or "classdef" in line.lower():
                print(f"Line {i}: {line}")

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
        converter.convert(str(self.md_file), "classdef")

        html_file = self.test_dir / "classdef.html"
        assert html_file.exists()

        html_content = html_file.read_text(encoding="utf-8")

        assert "flowchart TD" in html_content or "flowchart" in html_content
        assert "classDef" in html_content
        assert ":::" in html_content
        assert "🚀" in html_content

        print("\n=== HTML с classDef ===")
        start = html_content.find('<div class="mermaid">')
        if start != -1:
            end = html_content.find("</div>", start)
            diagram_html = html_content[start : end + 6]
            print(diagram_html[:1000])
            if len(diagram_html) > 1000:
                print("\n... (обрезано) ...")
                print(diagram_html[-500:])

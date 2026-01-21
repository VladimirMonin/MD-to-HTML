"""Тест для Mermaid classDiagram."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidClassDiagram:
    """Тесты для classDiagram с наследованием и note."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: ClassDiagram

```mermaid
classDiagram
    class BaseAI {
        <<abstract>>
        +config: Config
        #_client: Mistral
        +generate(prompt)*
        #_send_request(messages)
    }
    
    class TextGenerator {
        +system_prompt: str
        +previous_context: str
        +generate(prompt)
        -_build_messages(prompt)
        -_load_prompt()
    }
    
    BaseAI <|-- TextGenerator : наследует
    
    note for BaseAI "Отвечает за 'КАК отправить'\\n(транспортный слой)"
    note for TextGenerator "Отвечает за 'ЧТО отправить'\\n(слой логики)"
```
"""

        self.md_file = self.test_dir / "classdiagram.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_class_syntax(self):
        """Тест: препроцессор обрабатывает синтаксис класса."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем базовый синтаксис
        assert "classDiagram" in result
        assert "class BaseAI" in result
        assert "class TextGenerator" in result
        assert "<<abstract>>" in result

        print("\n=== ClassDiagram синтаксис ===")
        print(result[result.find("classDiagram") : result.find("classDiagram") + 500])

    def test_note_with_quotes(self):
        """Тест: note с кавычками и кириллицей."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что note остались
        assert "note for BaseAI" in result
        assert "note for TextGenerator" in result

        # Проверяем кириллицу в note
        assert "КАК отправить" in result or "'КАК отправить'" in result
        assert "ЧТО отправить" in result or "'ЧТО отправить'" in result

        print("\n=== Note директивы ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "note" in line.lower():
                print(f"Line {i}: {line}")

    def test_inheritance_with_label(self):
        """Тест: наследование с меткой на русском."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем синтаксис наследования
        assert "<|--" in result
        assert "наследует" in result

        print("\n=== Наследование ===")
        lines = result.split("\n")
        for line in lines:
            if "<|--" in line:
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
        converter.convert(str(self.md_file), "classdiagram")

        html_file = self.test_dir / "classdiagram.html"
        assert html_file.exists()

        html_content = html_file.read_text(encoding="utf-8")

        assert "classDiagram" in html_content
        assert "BaseAI" in html_content
        assert "TextGenerator" in html_content

        print("\n=== HTML ClassDiagram ===")
        start = html_content.find('<div class="mermaid">')
        if start != -1:
            end = html_content.find("</div>", start)
            print(html_content[start : end + 6])

"""Тест для Mermaid с множественными subgraph и inline styles."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidMultipleSubgraphs:
    """Тесты для диаграммы с 4 subgraph и style внутри subgraph."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: Множественные Subgraph

```mermaid
graph TD
    subgraph Step1 [Шаг 1: Чистый лист]
        C1[Чанк 1] -->|Вход| G1(Генерация)
        G1 --> R1["Результат: 'Классы...'"]
    end

    subgraph Step2 [Шаг 2: Накопление]
        R1 -.->|Сохраняем| MEM2[("Память: 'Классы...'")]
        MEM2 -->|Контекст| G2(Генерация Чанка 2)
        G2 --> R2["Результат: 'Методы...'"]
    end

    subgraph Step3 [Шаг 3: Насыщение]
        R2 -.->|Добавляем| MEM3[("Память: 'Классы... Методы...'")]
        MEM3 -->|Контекст| G3(Генерация Чанка 3)
        G3 --> R3["Результат: 'Наследование...'"]
    end

    subgraph Step4 [Шаг 4: Обрезка ✂️]
        R3 -.->|Места нет! Удаляем старое| MEM4[("Память: '...ды... Методы... Наследование...'")]
        style MEM4 fill:#ff6b6b,stroke:#c92a2a,color:#fff
        
        note["❌ 'Класс...' удалено<br>✅ '...ды...' осталось"]
        MEM4 -.- note
        
        MEM4 -->|Урезанный контекст| G4(Генерация Чанка 4)
    end

    style Step1 fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Step4 fill:#fff5f5,stroke:#ffcccc,stroke-width:2px
```
"""

        self.md_file = self.test_dir / "multiple_subgraphs.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_multiple_subgraphs(self):
        """Тест: обработка 4 subgraph."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем все subgraph
        assert "subgraph Step1" in result
        assert "subgraph Step2" in result
        assert "subgraph Step3" in result
        assert "subgraph Step4" in result

        print("\n=== Subgraph декларации ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "subgraph" in line:
                print(f"Line {i}: {line}")

    def test_style_inside_subgraph(self):
        """Тест: style директива внутри subgraph."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем style внутри subgraph
        assert "style MEM4" in result

        # Проверяем, что style после subgraph не поломан
        assert "style Step1" in result
        assert "style Step4" in result

        print("\n=== Style директивы ===")
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if "style" in line.lower():
                print(f"Line {i}: {line}")

    def test_emoji_in_subgraph_label(self):
        """Тест: эмодзи в метке subgraph."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что эмодзи остались
        assert "✂️" in result or "✂" in result
        assert "❌" in result
        assert "✅" in result

        print("\n=== Метки с эмодзи ===")
        lines = result.split("\n")
        for line in lines:
            if "✂" in line or "❌" in line or "✅" in line:
                print(line.strip())

    def test_database_node_with_quotes(self):
        """Тест: узлы с базой данных [( )] и кавычками внутри."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем узлы БД
        assert "[(" in result
        assert ")]" in result

        # Проверяем, что одинарные кавычки в тексте не сломали парсинг
        assert "Память:" in result
        assert "Классы..." in result

        print("\n=== Узлы базы данных ===")
        lines = result.split("\n")
        for line in lines:
            if "[(" in line or "Память" in line:
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
        converter.convert(str(self.md_file), "multiple_subgraphs")

        html_file = self.test_dir / "multiple_subgraphs.html"
        assert html_file.exists()

        html_content = html_file.read_text(encoding="utf-8")

        assert "graph TD" in html_content or "graph" in html_content
        assert "subgraph" in html_content
        assert "✂" in html_content or "&#" in html_content  # Эмодзи или entity

        print("\n=== HTML фрагмент ===")
        start = html_content.find('<div class="mermaid">')
        if start != -1:
            end = html_content.find("</div>", start)
            diagram_html = html_content[start : end + 6]
            print(diagram_html[:1500])  # Первые 1500 символов
            print("\n... (обрезано) ...")
            print(diagram_html[-500:])  # Последние 500 символов

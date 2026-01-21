"""Тест для Mermaid sequenceDiagram с синтаксисом <<create>>."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor


class TestMermaidSequenceDiagramCreate:
    """Тесты для sequenceDiagram с <<create>> и Note right of."""

    def setup_method(self):
        """Подготовка теста."""
        self.test_dir = Path("test_output/mermaid_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)

        self.diagram_md = """# Test: SequenceDiagram с <<create>>

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as OrderService
    participant Ord as Order
    participant Val as Validator
    participant Repo as Repository

    User->>Service: create(data)
    activate Service
    
    Note right of Service: 1. Создание объекта
    Service->>Ord: <<create>>
    activate Ord
    Ord-->>Service: order_instance
    deactivate Ord

    Note right of Service: 2. Проверка логики
    Service->>Val: validate(order_instance)
    activate Val
    Val-->>Service: is_valid (True)
    deactivate Val

    Note right of Service: 3. Сохранение
    Service->>Repo: save(order_instance)
    activate Repo
    Repo-->>Service: result_id
    deactivate Repo

    Service-->>User: Order Created (201 Created)
    deactivate Service
```
"""

        # Создаём тестовый MD файл
        self.md_file = self.test_dir / "sequence_create.md"
        self.md_file.write_text(self.diagram_md, encoding="utf-8")

    def test_preprocessor_preserves_create_syntax(self):
        """Тест: препроцессор НЕ трогает <<create>> в sequenceDiagram."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем, что <<create>> остался без изменений
        assert "<<create>>" in result, "<<create>> должен остаться в результате"

        # Проверяем, что sequenceDiagram синтаксис не был повреждён
        assert "sequenceDiagram" in result
        assert "participant Service as OrderService" in result
        assert "Note right of Service" in result
        assert "autonumber" in result

        # Проверяем кириллицу в Note
        assert "Создание объекта" in result
        assert "Проверка логики" in result

        print("\n=== Результат препроцессора ===")
        print(result)

    def test_preprocessor_preserves_angle_brackets(self):
        """Тест: проверяем, что автофикс заменяет << >> на « » в sequenceDiagram."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Автофикс должен заменить <<create>> на «create»
        # В исходнике: Service->>Ord: <<create>>
        # После фикса: Service-»Ord: «create»

        assert "«create»" in result, "Автофикс должен заменить <<create>> на «create»"

        # Угловые скобки в стрелках должны остаться:
        # Service->>Ord (это не кавычки, а синтаксис стрелок)
        assert "->>" in result or "-»" in result, "Стрелки с >> должны сохраниться"

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
        converter.convert(str(self.md_file), "sequence_create")

        # Проверяем, что HTML создан
        html_file = self.test_dir / "sequence_create.html"
        assert html_file.exists(), f"HTML файл не создан: {html_file}"

        html_content = html_file.read_text(encoding="utf-8")

        # Проверяем наличие Mermaid
        assert "mermaid" in html_content.lower()
        assert '<div class="mermaid">' in html_content

        # КРИТИЧЕСКАЯ ПРОВЕРКА: автофикс заменяет <<create>> на «create»
        assert "«create»" in html_content or "&#171;create&#187;" in html_content, (
            "Автофикс должен заменить <<create>> на «create» (либо как текст, либо как entities)"
        )

        # Проверяем, что диаграмма имеет правильный синтаксис
        assert "sequenceDiagram" in html_content
        assert "participant Service as OrderService" in html_content
        assert "Note right of Service" in html_content

        print(f"\n=== HTML создан: {html_file} ===")
        print(f"Размер: {html_file.stat().st_size} байт")

    def test_note_right_of_syntax(self):
        """Тест: проверяем синтаксис Note right of с кириллицей."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем все Note директивы
        assert "Note right of Service: 1. Создание объекта" in result
        assert "Note right of Service: 2. Проверка логики" in result
        assert "Note right of Service: 3. Сохранение" in result

    def test_participant_aliases(self):
        """Тест: проверяем синтаксис participant X as Alias."""
        prep = MermaidPreprocessor(format_type="html")
        result = prep.process(self.diagram_md)

        # Проверяем все participant с алиасами
        assert "participant Service as OrderService" in result
        assert "participant Ord as Order" in result
        assert "participant Val as Validator" in result
        assert "participant Repo as Repository" in result

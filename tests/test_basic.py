"""Тесты для новой архитектуры конвертера."""

import pytest
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import (
    ObsidianPreprocessor,
    CalloutsPreprocessor,
    MermaidPreprocessor,
    DiffPreprocessor,
)


def test_yaml_config():
    """Тест загрузки YAML конфига."""
    config = ConverterConfig.from_yaml("config.yaml")

    assert config.output_dir == "./build"
    assert isinstance(config.formats, list)
    assert config.template in ["book", "web"]
    assert config.media_mode in ["embed", "copy"]
    assert hasattr(config.features, "toc")


def test_obsidian_preprocessor():
    """Тест ObsidianPreprocessor."""
    prep = ObsidianPreprocessor()
    test_md = "![[image.png]] и [[link]]"
    result = prep.process(test_md)

    # Проверяем, что синтаксис преобразован (путь может измениться)
    assert "![](" in result and "image.png" in result
    assert "[link](link.md)" in result


def test_callouts_preprocessor():
    """Тест CalloutsPreprocessor."""
    prep = CalloutsPreprocessor()
    test_md = "> [!NOTE] Заголовок\n> Текст"
    result = prep.process(test_md)

    assert "::: NOTE" in result or "::: note" in result


def test_mermaid_preprocessor_html():
    """Тест MermaidPreprocessor для HTML."""
    prep = MermaidPreprocessor(format_type="html")
    test_md = "```mermaid\ngraph TD\n  A-->B\n```"
    result = prep.process(test_md)

    assert '<pre class="mermaid">' in result


def test_diff_preprocessor():
    """Тест DiffPreprocessor."""
    prep = DiffPreprocessor()
    test_md = "```diff-python\n---OLD---\nold code\n---NEW---\nnew code\n```"
    result = prep.process(test_md)

    assert "Было:" in result
    assert "Стало:" in result
    assert "diff-wrapper" in result


def test_basic_conversion():
    """Тест базовой конвертации MD → HTML."""
    config = ConverterConfig()
    config.formats = ["html"]
    config.output_dir = "build"
    config.metadata.title = "Тестовый документ"
    config.metadata.author = "Test"

    converter = Converter(config)
    results = converter.convert("doc/README.md", "test_output")

    assert len(results) > 0, "Должен быть создан хотя бы один файл"
    for path in results:
        assert path.exists(), f"Файл не создан: {path}"
        assert path.suffix in [".html", ".epub"]
    diff = DiffPreprocessor()
    test_md = "```diff-python\n---OLD---\nold code\n---NEW---\nnew code\n```"
    result = diff.process(test_md)
    print(f"Diff: {test_md[:30]}... → {result[:50]}...")
    assert "Было:" in result
    assert "Стало:" in result
    print("  ✅ DiffPreprocessor")

    print("\n✅ Все препроцессоры работают!\n")


if __name__ == "__main__":
    print("\n" + "🚀 ЗАПУСК ТЕСТОВ НОВОЙ АРХИТЕКТУРЫ 🚀".center(60))

    try:
        test_yaml_config()
        test_preprocessors()
        test_basic_conversion()

        print("\n" + "🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! 🎉".center(60) + "\n")

    except Exception as e:
        print(f"\n❌ ТЕСТ ПРОВАЛЕН:\n")
        import traceback

        traceback.print_exc()

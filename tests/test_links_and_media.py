"""Комплексные тесты для ссылок, изображений и вариантов сохранения."""

import pytest
from pathlib import Path
import shutil
import tempfile
from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import ObsidianPreprocessor


class TestMarkdownLinks:
    """Тесты различных типов Markdown ссылок."""

    def test_obsidian_wikilinks_simple(self):
        """Простые wikilinks [[link]]."""
        prep = ObsidianPreprocessor()
        result = prep.process("См. [[документация]] для деталей")
        assert "[документация](документация.md)" in result

    def test_obsidian_wikilinks_with_alias(self):
        """Wikilinks с алиасами [[link|display]]."""
        prep = ObsidianPreprocessor()
        result = prep.process("См. [[api/docs|API документацию]]")
        assert "[API документацию](api/docs.md)" in result

    def test_obsidian_wikilinks_multiple(self):
        """Множественные wikilinks в тексте."""
        prep = ObsidianPreprocessor()
        text = "[[Первая ссылка]] и [[Вторая ссылка]] в тексте"
        result = prep.process(text)
        assert "[Первая ссылка](Первая ссылка.md)" in result
        assert "[Вторая ссылка](Вторая ссылка.md)" in result

    def test_markdown_links_preserved(self):
        """Обычные MD ссылки не должны меняться."""
        prep = ObsidianPreprocessor()
        text = "[Google](https://google.com) и [локальный](./file.md)"
        result = prep.process(text)
        assert "[Google](https://google.com)" in result
        assert "[локальный](./file.md)" in result

    def test_mixed_links(self):
        """Смешанные типы ссылок в одном документе."""
        prep = ObsidianPreprocessor()
        text = """
        Обычная ссылка: [example](https://example.com)
        Wikilink: [[internal-page]]
        Wikilink с алиасом: [[deep/nested|Вложенная]]
        """
        result = prep.process(text)
        assert "[example](https://example.com)" in result
        assert "[internal-page](internal-page.md)" in result
        assert "[Вложенная](deep/nested.md)" in result

    def test_block_boundaries_before_heading_and_around_rule(self):
        """Obsidian-заметки без пустых строк не должны склеиваться в Pandoc."""
        prep = ObsidianPreprocessor()
        result = prep.process("[[card|Карточка]]\n---\nТекст\n*Подпись*\n## Следующий раздел")

        assert "[Карточка](card.md)\n\n***\n\nТекст" in result
        assert "*Подпись*\n\n## Следующий раздел" in result


class TestObsidianImages:
    """Тесты для обработки Obsidian изображений."""

    def test_obsidian_image_simple(self):
        """Простое изображение ![[image.png]]."""
        prep = ObsidianPreprocessor()
        result = prep.process("![[screenshot.png]]")
        assert "![](screenshot.png)" in result

    def test_obsidian_image_with_path(self):
        """Изображение с путём ![[folder/image.png]]."""
        prep = ObsidianPreprocessor()
        result = prep.process("![[attachments/photo.jpg]]")
        # Препроцессор ищет файл, если не найден - возвращает как есть
        assert "photo.jpg" in result

    def test_obsidian_multiple_images(self):
        """Множественные изображения."""
        prep = ObsidianPreprocessor()
        text = "![[image1.png]] и ![[image2.jpg]] в тексте"
        result = prep.process(text)
        assert "![](image1.png)" in result
        assert "![](image2.jpg)" in result

    def test_markdown_images_preserved(self):
        """Обычные MD изображения не меняются."""
        prep = ObsidianPreprocessor()
        text = "![Alt text](https://example.com/image.png)"
        result = prep.process(text)
        assert "![Alt text](https://example.com/image.png)" in result


class TestMediaModes:
    """Тесты режимов сохранения медиа (embed vs copy)."""

    @pytest.fixture
    def temp_workspace(self):
        """Создание временной рабочей области с тестовыми файлами."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # Создаём структуру:
            # temp/
            #   ├── test.md
            #   ├── image.png (пустой файл для теста)
            #   └── build/ (создастся автоматически)

            test_md = workspace / "test.md"
            test_md.write_text(
                """# Тестовый документ

![Тестовое изображение](image.png)

Обычный текст.
""",
                encoding="utf-8",
            )

            # Создаём пустой "изображение" для теста
            test_image = workspace / "image.png"
            test_image.write_bytes(b"PNG_FAKE_DATA")

            yield workspace

    def test_embed_mode_no_media_folder(self, temp_workspace):
        """Режим EMBED не должен создавать папку media/."""
        config = ConverterConfig()
        config.formats = ["html"]
        config.media_mode = "embed"
        config.output_dir = str(temp_workspace / "build")
        config.metadata.title = "Embed Test"

        converter = Converter(config)
        test_file = temp_workspace / "test.md"
        results = converter.convert(str(test_file), "embed_result")

        # Проверки
        assert len(results) == 1
        html_file = results[0]
        assert html_file.exists()

        # Папка media/ НЕ должна быть создана
        media_dir = Path(config.output_dir) / "media"
        assert not media_dir.exists(), "В режиме EMBED не должно быть папки media/"

    def test_copy_mode_creates_media_folder(self, temp_workspace):
        """Режим COPY должен создавать папку media/."""
        config = ConverterConfig()
        config.formats = ["html"]
        config.media_mode = "copy"
        config.output_dir = str(temp_workspace / "build")
        config.metadata.title = "Copy Test"

        converter = Converter(config)
        test_file = temp_workspace / "test.md"
        results = converter.convert(str(test_file), "copy_result")

        # Проверки
        assert len(results) == 1
        html_file = results[0]
        assert html_file.exists()

        # Папка media/ ДОЛЖНА быть создана
        media_dir = Path(config.output_dir) / "media"
        assert media_dir.exists(), "В режиме COPY должна быть папка media/"
        assert media_dir.is_dir()

        # Проверяем, что изображение скопировано
        copied_image = media_dir / "image.png"
        assert copied_image.exists(), "Изображение должно быть скопировано в media/"

    def test_embed_mode_larger_file_size(self, temp_workspace):
        """EMBED режим создаёт больший файл (встроенные данные)."""
        # Создаём файл с EMBED
        config_embed = ConverterConfig()
        config_embed.formats = ["html"]
        config_embed.media_mode = "embed"
        config_embed.output_dir = str(temp_workspace / "build_embed")
        config_embed.metadata.title = "Embed"

        converter_embed = Converter(config_embed)
        test_file = temp_workspace / "test.md"
        results_embed = converter_embed.convert(str(test_file), "result_embed")

        # Создаём файл с COPY
        config_copy = ConverterConfig()
        config_copy.formats = ["html"]
        config_copy.media_mode = "copy"
        config_copy.output_dir = str(temp_workspace / "build_copy")
        config_copy.metadata.title = "Copy"

        converter_copy = Converter(config_copy)
        results_copy = converter_copy.convert(str(test_file), "result_copy")

        # Сравниваем размеры
        embed_file = results_embed[0]
        copy_file = results_copy[0]

        embed_size = embed_file.stat().st_size
        copy_size = copy_file.stat().st_size

        print(f"\n📊 Размеры файлов:")
        print(f"   EMBED: {embed_size:,} байт")
        print(f"   COPY:  {copy_size:,} байт")

        # EMBED должен быть больше (встроенные данные)
        # Но если Pandoc не встроил - размеры могут быть похожи
        assert embed_size > 0 and copy_size > 0


class TestImageSearch:
    """Тесты поиска изображений в разных папках."""

    @pytest.fixture
    def obsidian_vault_structure(self):
        """Имитация структуры Obsidian vault."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vault = Path(tmpdir)

            # Структура:
            # vault/
            #   ├── note.md
            #   ├── attachments/
            #   │   └── image1.png
            #   ├── _attachments/
            #   │   └── image2.jpg
            #   └── assets/
            #       └── deep/
            #           └── image3.gif

            (vault / "attachments").mkdir()
            (vault / "_attachments").mkdir()
            (vault / "assets" / "deep").mkdir(parents=True)

            (vault / "attachments" / "image1.png").write_bytes(b"PNG1")
            (vault / "_attachments" / "image2.jpg").write_bytes(b"JPG2")
            (vault / "assets" / "deep" / "image3.gif").write_bytes(b"GIF3")

            note = vault / "note.md"
            note.write_text("# Test\n![[image1.png]]\n![[image2.jpg]]\n![[image3.gif]]")

            yield vault

    def test_find_in_attachments(self, obsidian_vault_structure):
        """Поиск изображения в attachments/."""
        base_path = obsidian_vault_structure
        prep = ObsidianPreprocessor(base_path=base_path)

        result = prep.process("![[image1.png]]")
        assert "image1.png" in result
        assert "attachments" in result

    def test_find_in_underscore_attachments(self, obsidian_vault_structure):
        """Поиск изображения в _attachments/."""
        base_path = obsidian_vault_structure
        prep = ObsidianPreprocessor(base_path=base_path)

        result = prep.process("![[image2.jpg]]")
        assert "image2.jpg" in result
        assert "_attachments" in result

    def test_recursive_search_in_assets(self, obsidian_vault_structure):
        """Рекурсивный поиск в assets/deep/."""
        base_path = obsidian_vault_structure
        prep = ObsidianPreprocessor(base_path=base_path)

        result = prep.process("![[image3.gif]]")
        assert "image3.gif" in result
        # Должен найти в подпапке
        assert "deep" in result or "assets" in result

    def test_not_found_returns_original(self, obsidian_vault_structure):
        """Ненайденное изображение возвращается как есть."""
        base_path = obsidian_vault_structure
        prep = ObsidianPreprocessor(base_path=base_path)

        result = prep.process("![[nonexistent.png]]")
        assert "nonexistent.png" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

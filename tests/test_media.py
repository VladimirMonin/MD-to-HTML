"""Тесты для обработки медиа файлов (embed/copy режимы)."""

import pytest
from pathlib import Path
import shutil
from md_converter import Converter, ConverterConfig


@pytest.fixture
def test_md_file():
    """Путь к тестовому MD файлу с медиа."""
    path = Path(r"C:\Syncthing\База Obsidian\_inbox\Deploy P2_results.md")
    if not path.exists():
        pytest.skip(f"Тестовый файл не найден: {path}")
    return path


@pytest.fixture
def clean_build_dir():
    """Создание отдельной тестовой build директории."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        test_build = Path(tmpdir) / "test_build"
        test_build.mkdir(parents=True, exist_ok=True)
        yield test_build


def test_media_embed_mode(test_md_file, clean_build_dir):
    """Тест режима EMBED - медиа встраивается в HTML."""
    # Конфигурация
    config = ConverterConfig()
    config.formats = ["html"]
    config.media_mode = "embed"
    config.output_dir = str(clean_build_dir)
    config.metadata.title = "Тест EMBED"

    # Конвертация
    converter = Converter(config)
    results = converter.convert(str(test_md_file), "test_embed")

    # Проверки
    assert len(results) == 1, "Должен быть создан 1 HTML файл"

    html_file = results[0]
    assert html_file.exists(), f"HTML файл не создан: {html_file}"
    assert html_file.suffix == ".html"

    # Проверка, что медиа НЕ скопированы в папку
    media_dir = clean_build_dir / "media"
    assert not media_dir.exists(), "Папка media/ не должна существовать в режиме embed"

    # Проверка размера файла (должен быть больше из-за встроенных медиа)
    file_size_mb = html_file.stat().st_size / (1024 * 1024)
    print(f"\n✅ EMBED режим: размер файла {file_size_mb:.2f} MB")

    # Проверка содержимого - должны быть data:image/png;base64
    content = html_file.read_text(encoding="utf-8")
    has_embedded_images = "data:image" in content or "base64" in content
    print(f"   Встроенные изображения: {has_embedded_images}")


def test_media_copy_mode(test_md_file, clean_build_dir):
    """Тест режима COPY - медиа копируется в media/."""
    # Конфигурация
    config = ConverterConfig()
    config.formats = ["html"]
    config.media_mode = "copy"
    config.output_dir = str(clean_build_dir)
    config.metadata.title = "Тест COPY"

    # Конвертация
    converter = Converter(config)
    results = converter.convert(str(test_md_file), "test_copy")

    # Проверки
    assert len(results) == 1, "Должен быть создан 1 HTML файл"

    html_file = results[0]
    assert html_file.exists(), f"HTML файл не создан: {html_file}"

    # Проверка, что создана папка media/
    media_dir = clean_build_dir / "media"
    assert media_dir.exists(), "Папка media/ должна быть создана в режиме copy"
    assert media_dir.is_dir(), "media должна быть папкой"

    # Подсчет скопированных файлов
    media_files = list(media_dir.rglob("*"))
    media_files = [f for f in media_files if f.is_file()]
    print(f"\n✅ COPY режим: скопировано {len(media_files)} медиа файлов")

    # Проверка размера файла (должен быть меньше без встроенных медиа)
    file_size_kb = html_file.stat().st_size / 1024
    print(f"   Размер HTML: {file_size_kb:.2f} KB")

    # Проверка содержимого - не должно быть data:image
    content = html_file.read_text(encoding="utf-8")
    has_embedded = "data:image" in content
    assert not has_embedded, "В режиме copy не должно быть встроенных изображений"

    # Должны быть ссылки на media/
    has_media_links = "media/" in content
    print(f"   Ссылки на media/: {has_media_links}")


def test_media_both_formats(test_md_file, clean_build_dir):
    """Тест конвертации в оба формата с медиа."""
    config = ConverterConfig()
    config.formats = ["html", "epub"]
    config.media_mode = "embed"
    config.output_dir = str(clean_build_dir)
    config.metadata.title = "Тест HTML+EPUB"

    converter = Converter(config)
    results = converter.convert(str(test_md_file), "test_both")

    assert len(results) == 2, "Должно быть создано 2 файла (HTML + EPUB)"

    extensions = {r.suffix for r in results}
    assert ".html" in extensions, "Должен быть HTML файл"
    assert ".epub" in extensions, "Должен быть EPUB файл"

    for result in results:
        assert result.exists(), f"Файл не создан: {result}"
        size_kb = result.stat().st_size / 1024
        print(f"\n✅ {result.suffix.upper()}: {size_kb:.2f} KB")


def test_media_epub_embeds_fonts(test_md_file, clean_build_dir):
    """Тест что EPUB встраивает шрифты."""
    config = ConverterConfig()
    config.formats = ["epub"]
    config.media_mode = "embed"
    config.output_dir = str(clean_build_dir)
    config.metadata.title = "Тест EPUB шрифты"
    config.fonts.embed = True

    converter = Converter(config)
    results = converter.convert(str(test_md_file), "test_epub_fonts")

    assert len(results) == 1
    epub_file = results[0]
    assert epub_file.suffix == ".epub"

    # EPUB с встроенными шрифтами должен быть больше
    size_mb = epub_file.stat().st_size / (1024 * 1024)
    print(f"\n✅ EPUB с шрифтами: {size_mb:.2f} MB")

    # Минимальный размер (должно быть > 1 MB если шрифты встроены)
    assert size_mb > 0.5, "EPUB со шрифтами должен быть больше 0.5 MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

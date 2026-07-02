#!/usr/bin/env python3
"""CLI для MD-to-HTML конвертера."""

import argparse
import sys
from pathlib import Path

try:
    from md_converter import Converter, ConverterConfig
except ImportError:
    # Если запускаем из корня проекта
    sys.path.insert(0, str(Path(__file__).parent))
    from md_converter import Converter, ConverterConfig


def main():
    parser = argparse.ArgumentParser(
        prog="md-convert",
        description="Конвертер Markdown в HTML/EPUB с профессиональным оформлением",
    )

    # Позиционные аргументы
    parser.add_argument("input", help="Путь к MD файлу или папке")
    parser.add_argument("-o", "--output", help="Имя выходного файла (без расширения)")

    # Форматы
    parser.add_argument(
        "-f",
        "--format",
        choices=["html", "epub", "both"],
        default="html",
        help="Выходной формат (default: html)",
    )

    # Режим медиа
    parser.add_argument(
        "-m",
        "--media",
        choices=["embed", "copy"],
        default="embed",
        help="Режим медиа: embed (в файл) или copy (в папку media/)",
    )

    # Шаблон
    parser.add_argument(
        "-t",
        "--template",
        choices=["book", "web"],
        default="book",
        help="HTML шаблон (default: book)",
    )

    # Конфиг файл
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Путь к YAML конфигу (default: config.yaml)",
    )

    # Метаданные
    parser.add_argument("--title", help="Заголовок документа")
    parser.add_argument("--author", help="Автор")
    parser.add_argument("--brand", help="Путь к обложке")

    # Фичи
    parser.add_argument("--no-toc", action="store_true", help="Отключить оглавление")
    parser.add_argument(
        "--no-breadcrumbs", action="store_true", help="Отключить breadcrumbs"
    )
    parser.add_argument("--no-mermaid", action="store_true", help="Отключить Mermaid")
    parser.add_argument(
        "--mermaid-panzoom",
        action="store_true",
        help="Включить SVG pan/zoom для Mermaid (только HTML + --media copy)",
    )

    # Тема
    parser.add_argument(
        "--theme",
        default="github-dark",
        help="Тема подсветки кода (default: github-dark)",
    )

    args = parser.parse_args()

    # Загрузка базового конфига
    config_path = Path(args.config)
    if config_path.exists():
        config = ConverterConfig.from_yaml(config_path)
        print(f"✅ Загружен конфиг: {config_path}\n")
    else:
        config = ConverterConfig()
        print(f"⚠️ Конфиг {config_path} не найден, используем настройки по умолчанию\n")

    # Переопределение из CLI
    config.input.path = args.input
    config.media_mode = args.media
    config.template = args.template
    config.formats = ["html", "epub"] if args.format == "both" else [args.format]

    if args.title:
        config.metadata.title = args.title
    if args.author:
        config.metadata.author = args.author
    if args.brand:
        config.metadata.brand_image = args.brand
    if args.theme:
        config.styles.highlight_theme = args.theme

    config.features.toc = not args.no_toc
    config.features.breadcrumbs = not args.no_breadcrumbs
    config.features.mermaid = not args.no_mermaid
    config.features.mermaid_panzoom = args.mermaid_panzoom

    # Конвертация
    converter = Converter(config)
    try:
        results = converter.convert(args.input, args.output)

        print(f"\n{'=' * 60}")
        print("🎉 Конвертация завершена успешно!")
        print(f"{'=' * 60}")
        print("\n📦 Созданные файлы:")
        for path in results:
            print(f"  ✓ {path}")
        print()

    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ Ошибка конвертации")
        print(f"{'=' * 60}")
        print(f"\n{e}\n", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

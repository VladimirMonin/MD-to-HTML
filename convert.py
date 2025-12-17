#!/usr/bin/env python3
"""
Интерактивное меню для MD-to-HTML конвертера.
Пошаговое ведение пользователя через процесс конвертации.
"""

import sys
from pathlib import Path
from typing import Optional

try:
    from md_converter import Converter, ConverterConfig
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from md_converter import Converter, ConverterConfig


def print_header():
    """Печать заголовка."""
    print("\n" + "=" * 60)
    print("📚 MD-to-HTML Converter v2.0 - Интерактивное меню")
    print("=" * 60 + "\n")


def input_path() -> str:
    """Запрос пути к файлу/папке."""
    print("📁 Шаг 1: Исходные данные")
    print("-" * 60)
    while True:
        path = input("Путь к MD файлу или папке: ").strip().strip("\"'")
        if Path(path).exists():
            return path
        print("❌ Путь не найден. Попробуйте снова.\n")


def input_format() -> list[str]:
    """Выбор формата выходного файла."""
    print("\n📦 Шаг 2: Формат")
    print("-" * 60)
    print("1. HTML")
    print("2. EPUB")
    print("3. Оба (HTML + EPUB)")

    while True:
        choice = input("\nВыбор (1-3): ").strip()
        if choice == "1":
            return ["html"]
        elif choice == "2":
            return ["epub"]
        elif choice == "3":
            return ["html", "epub"]
        print("❌ Неверный выбор. Введите 1, 2 или 3.\n")


def input_media_mode() -> str:
    """Выбор режима обработки медиа."""
    print("\n🖼️ Шаг 3: Медиа файлы")
    print("-" * 60)
    print("1. EMBED - встроить в HTML (самодостаточный файл)")
    print("2. COPY - скопировать в папку media/ (меньше размер)")

    while True:
        choice = input("\nВыбор (1-2): ").strip()
        if choice == "1":
            return "embed"
        elif choice == "2":
            return "copy"
        print("❌ Неверный выбор. Введите 1 или 2.\n")


def input_template() -> str:
    """Выбор HTML шаблона."""
    print("\n🎨 Шаг 4: Шаблон оформления")
    print("-" * 60)
    print("1. BOOK - книжный вид (минималистичный, для чтения)")
    print("2. WEB - веб вид (Bootstrap, sidebar с TOC)")

    while True:
        choice = input("\nВыбор (1-2): ").strip()
        if choice == "1":
            return "book"
        elif choice == "2":
            return "web"
        print("❌ Неверный выбор. Введите 1 или 2.\n")


def input_metadata() -> dict:
    """Запрос метаданных."""
    print("\n📝 Шаг 5: Метаданные (опционально)")
    print("-" * 60)
    print("Нажмите Enter, чтобы пропустить")

    title = input("Заголовок документа: ").strip()
    author = input("Автор: ").strip()
    brand = input("Путь к обложке (изображение): ").strip().strip("\"'")

    metadata = {}
    if title:
        metadata["title"] = title
    if author:
        metadata["author"] = author
    if brand and Path(brand).exists():
        metadata["brand_image"] = brand

    return metadata


def input_features() -> dict:
    """Настройка дополнительных функций."""
    print("\n⚙️ Шаг 6: Дополнительные функции")
    print("-" * 60)
    print("Включить все по умолчанию? (y/n): ", end="")

    if input().strip().lower() == "y":
        return {}

    print("\nОтключить функции (Enter = оставить включенной):")
    features = {}

    if input("  Оглавление (TOC)? (y/N): ").strip().lower() == "n":
        features["toc"] = False
    if input("  Хлебные крошки (Breadcrumbs)? (y/N): ").strip().lower() == "n":
        features["breadcrumbs"] = False
    if input("  Mermaid диаграммы? (y/N): ").strip().lower() == "n":
        features["mermaid"] = False
    if input("  Кнопки копирования кода? (y/N): ").strip().lower() == "n":
        features["code_copy"] = False

    return features


def confirm_settings(config: ConverterConfig, input_path_val: str) -> bool:
    """Подтверждение настроек."""
    print("\n" + "=" * 60)
    print("📋 Итоговые настройки")
    print("=" * 60)
    print(f"📁 Источник: {input_path_val}")
    print(f"📦 Форматы: {', '.join(config.formats).upper()}")
    print(f"🖼️ Медиа: {config.media_mode.upper()}")
    print(f"🎨 Шаблон: {config.template.upper()}")
    if config.metadata.title:
        print(f"📝 Заголовок: {config.metadata.title}")
    if config.metadata.author:
        print(f"✍️ Автор: {config.metadata.author}")
    print(f"📂 Выходная папка: {config.output_dir}")
    print("=" * 60)

    confirm = input("\n✅ Начать конвертацию? (y/N): ").strip().lower()
    return confirm == "y"


def main():
    """Главная функция интерактивного меню."""
    print_header()

    # Загрузка базового конфига
    config_path = Path("config.yaml")
    if config_path.exists():
        config = ConverterConfig.from_yaml(config_path)
        print("✅ Загружен config.yaml\n")
    else:
        config = ConverterConfig()
        print("⚠️ config.yaml не найден, используем настройки по умолчанию\n")

    # Шаги
    input_path_val = input_path()
    config.formats = input_format()
    config.media_mode = input_media_mode()
    config.template = input_template()

    metadata = input_metadata()
    if metadata.get("title"):
        config.metadata.title = metadata["title"]
    if metadata.get("author"):
        config.metadata.author = metadata["author"]
    if metadata.get("brand_image"):
        config.metadata.brand_image = metadata["brand_image"]

    features = input_features()
    for key, value in features.items():
        setattr(config.features, key, value)

    # Подтверждение
    if not confirm_settings(config, input_path_val):
        print("\n❌ Конвертация отменена.\n")
        return

    # Конвертация
    print("\n" + "=" * 60)
    print("🚀 Запуск конвертации...")
    print("=" * 60 + "\n")

    converter = Converter(config)
    try:
        results = converter.convert(input_path_val)

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
        print(f"\n{e}\n")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем.\n")
        sys.exit(0)

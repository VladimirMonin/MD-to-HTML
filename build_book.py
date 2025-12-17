import os
import subprocess
import re
from natsort import natsorted

# --- КОНФИГУРАЦИЯ (ТВОИ ПЕРЕМЕННЫЕ) ---

# Папка, где лежат .md файлы (скрипт соберет их все)
INPUT_FOLDER = "./content"

# Название выходного файла (без расширения)
OUTPUT_FILENAME = "My_Django_Notes"

# Папка для результата
OUTPUT_FOLDER = "./build"

# Файл стилей
CSS_FILE = "book_style.css"

# Путь к шрифтам (для внедрения в EPUB/HTML)
FONTS_DIR = "./assets/fonts"

# --- ФУНКЦИИ ---


def preprocess_markdown(content):
    """
    Превращает Obsidian Callouts (> [!INFO]) в Pandoc Divs (::: info)
    чтобы мы могли их стилизовать в CSS.
    """
    # Паттерн: > [!TYPE] Title (опционально)
    #          > Content...

    # Простая замена заголовков блоков (для примера обрабатываем note, tip, warning, danger)
    # Превращаем: > [!TIP] Заголовок
    # В: ::: tip
    #    **Заголовок**

    # 1. Заменяем открытие блока
    content = re.sub(
        r">\s*\[!(NOTE|INFO|TIP|WARNING|DANGER|ERROR)\]\s*(.*)",
        r"\n::: \1\n**\2**\n",
        content,
        flags=re.IGNORECASE,
    )

    # 2. Очищаем символы цитирования "> " внутри блока (упрощенная логика)
    # В идеале лучше использовать Lua-фильтр, но для начала хватит regex
    # Pandoc умный, он поймет ::: если мы закроем его в конце файла или перед след заголовком
    # Но для надежности лучше просто использовать нативный синтаксис Pandoc ::: class в MD файлах

    # ДЛЯ СОВМЕСТИМОСТИ С OBSIDIAN:
    # Лучший способ - использовать плагин 'obsidian-export' или просто вручную добавлять ::: в конце.
    # Но давай сделаем хак: добавим закрытие ::: перед следующим заголовком или в конце

    return content


def get_merged_content(folder_path):
    """Читает все MD файлы, сортирует и склеивает в один текст"""
    all_md_files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    # Сортируем (Глава 1, Глава 2, Глава 10...)
    sorted_files = natsorted(all_md_files)

    merged_content = ""
    print(f"--- Сшиваем файлы ({len(sorted_files)} шт) ---")

    for filename in sorted_files:
        path = os.path.join(folder_path, filename)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            # Добавляем разрыв страниц перед каждым файлом (для PDF/EPUB полезно)
            merged_content += f"\n\n\\newpage\n\n"
            merged_content += text + "\n"
            print(f" + {filename}")

    return preprocess_markdown(merged_content)


def build_book(format_type):
    # 1. Сшиваем контент
    full_text = get_merged_content(INPUT_FOLDER)

    # 2. Сохраняем временный "Мега-файл"
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    temp_md = os.path.join(OUTPUT_FOLDER, "_temp_merged.md")

    with open(temp_md, "w", encoding="utf-8") as f:
        f.write(full_text)

    # 3. Формируем команду Pandoc
    output_ext = "epub" if format_type == "epub" else "html"
    output_file = os.path.join(OUTPUT_FOLDER, f"{OUTPUT_FILENAME}.{output_ext}")

    cmd = [
        "pandoc",
        temp_md,
        "-o",
        output_file,
        "--standalone",
        "--toc",  # Оглавление
        "--toc-depth=2",
        "--embed-resources",  # Вшить всё внутрь
        "--css",
        CSS_FILE,  # Наши стили
        "--filter",
        "mermaid-filter",  # Диаграммы
    ]

    if format_type == "epub":
        cmd.append("--to=epub3")
    else:
        cmd.append("--to=html5")

    print(f"\nЗапуск Pandoc для {format_type.upper()}...")
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Готово! Файл: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    print("1. Собрать HTML (Single File)")
    print("2. Собрать EPUB")
    choice = input("Выбор: ")

    if choice == "1":
        build_book("html")
    elif choice == "2":
        build_book("epub")

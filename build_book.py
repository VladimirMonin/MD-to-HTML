import os
import subprocess
import re
from natsort import natsorted

# --- КОНФИГУРАЦИЯ (ТВОИ ПЕРЕМЕННЫЕ) ---

# Папка для результата
OUTPUT_FOLDER = "./build"

# Файл стилей (относительный путь от корня проекта)
CSS_FILE = "assets/css/book_style.css"

# Путь к шрифтам (для внедрения в EPUB/HTML)
FONTS_DIR = "./assets/fonts"

# --- ФУНКЦИИ ---


def preprocess_markdown(content):
    """
    Подготавливает markdown для Pandoc:
    1. Превращает Obsidian Callouts в Pandoc Divs
    2. Обрабатывает Mermaid диаграммы для корректного рендера
    """
    # 1. Обработка Obsidian Callouts
    content = re.sub(
        r">\s*\[!(NOTE|INFO|TIP|WARNING|DANGER|ERROR)\]\s*(.*)",
        r"\n::: \1\n**\2**\n",
        content,
        flags=re.IGNORECASE,
    )

    # 2. Обработка Mermaid диаграмм
    # Находим все блоки ```mermaid и оборачиваем в правильный div
    def replace_mermaid(match):
        mermaid_code = match.group(1)
        return f'<pre class="mermaid">\n{mermaid_code}\n</pre>'

    # Заменяем ```mermaid...``` на <pre class="mermaid">...</pre>
    content = re.sub(
        r"```mermaid\n(.*?)\n```", replace_mermaid, content, flags=re.DOTALL
    )

    return content


def get_merged_content(input_path, format_type="html"):
    """Читает MD файл(ы), сортирует и склеивает в один текст"""
    merged_content = ""

    if os.path.isfile(input_path):
        # Один файл
        print(f"--- Обрабатываем файл: {os.path.basename(input_path)} ---")
        with open(input_path, "r", encoding="utf-8") as f:
            merged_content = f.read()
    elif os.path.isdir(input_path):
        # Папка с файлами
        all_md_files = [f for f in os.listdir(input_path) if f.endswith(".md")]
        sorted_files = natsorted(all_md_files)

        print(f"--- Сшиваем файлы ({len(sorted_files)} шт) ---")
        for filename in sorted_files:
            path = os.path.join(input_path, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                # Для EPUB не добавляем разделители вообще
                if format_type != "epub":
                    merged_content += "\n\n"
                merged_content += text + "\n"
                print(f" + {filename}")
    else:
        raise ValueError(f"Путь не существует: {input_path}")

    return preprocess_markdown(merged_content)


def build_book(input_path, output_filename, format_type):
    # 1. Сшиваем контент
    full_text = get_merged_content(input_path, format_type)

    # 2. Сохраняем временный "Мега-файл"
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    temp_md = os.path.join(OUTPUT_FOLDER, "_temp_merged.md")

    with open(temp_md, "w", encoding="utf-8") as f:
        f.write(full_text)

    # 3. Формируем команду Pandoc
    output_ext = "epub" if format_type == "epub" else "html"
    output_file = os.path.join(OUTPUT_FOLDER, f"{output_filename}.{output_ext}")

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
    ]

    # Для HTML добавляем mermaid.js
    if format_type == "html":
        mermaid_header = os.path.join(OUTPUT_FOLDER, "_mermaid_header.html")
        with open(mermaid_header, "w", encoding="utf-8") as f:
            f.write("""<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true, theme: 'default' });
</script>""")
        cmd.extend(["--include-in-header", mermaid_header])
        cmd.append("--to=html5")
    else:
        cmd.append("--to=epub3")

    print(f"\nЗапуск Pandoc для {format_type.upper()}...")
    print(f"Команда: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Готово! Файл: {output_file}")
        if result.stdout:
            print(f"Вывод: {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка Pandoc: {e}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")


if __name__ == "__main__":
    # Запрашиваем путь к файлу или папке
    input_path = (
        input(r"Введите путь к файлу .md или папке с файлами: ")
        .replace('"', "")
        .replace("'", "")
        .strip()
    )
    abs_input_path = os.path.abspath(input_path)

    if not os.path.exists(abs_input_path):
        print(f"❌ Путь не существует: {abs_input_path}")
        exit(1)

    # Определяем имя выходного файла
    if os.path.isfile(abs_input_path):
        default_name = os.path.splitext(os.path.basename(abs_input_path))[0]
    else:
        default_name = os.path.basename(abs_input_path.rstrip(os.sep))

    output_name = input(
        f"Название выходного файла (без расширения) [{default_name}]: "
    ).strip()
    if not output_name:
        output_name = default_name

    print("\n1. Собрать HTML")
    print("2. Собрать EPUB")
    print("3. Собрать HTML + EPUB")
    choice = input("Выбор: ")

    if choice == "1":
        build_book(abs_input_path, output_name, "html")
    elif choice == "2":
        build_book(abs_input_path, output_name, "epub")
    elif choice == "3":
        print("\n=== Сборка HTML ===")
        build_book(abs_input_path, output_name, "html")
        print("\n=== Сборка EPUB ===")
        build_book(abs_input_path, output_name, "epub")
    else:
        print("Неверный выбор")

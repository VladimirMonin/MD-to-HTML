import os
import subprocess
import re
from natsort import natsorted

# --- КОНФИГУРАЦИЯ (ТВОИ ПЕРЕМЕННЫЕ) ---

# Папка для результата
OUTPUT_FOLDER = "./build"

# Файл стилей (относительный путь от корня проекта)
CSS_FILE = "assets/css/book_style.css"

# Путь к шрифтам (для внедрения в EPUB)
FONTS_DIR = "./assets/fonts"

# Вшивать ли шрифты в EPUB (PocketBook и другие читалки могут не видеть шрифты без этого)
EMBED_FONTS_IN_EPUB = True

# Кастомная тема подсветки синтаксиса (github-dark.theme в assets/)
# Это JSON файл, созданный через pandoc --print-highlight-style
CUSTOM_THEME_FILE = "assets/github-dark.theme"

# Или можно использовать встроенные темы Pandoc Skylighting:
AVAILABLE_HIGHLIGHT_STYLES = [
    "pygments",  # Классическая тема Python
    "tango",  # Яркие цвета на светлом фоне
    "espresso",  # Тёмная тема с тёплыми оттенками
    "zenburn",  # Тёмная тема, мягкие цвета (низкий контраст)
    "kate",  # Светлая тема (как в Kate редакторе)
    "monochrome",  # Чёрно-белая
    "breezedark",  # Тёмная тема KDE Breeze
    "haddock",  # Светлая тема Haskell Haddock
]

# Mermaid-filter настройки (для EPUB)
# SVG даёт лучшее качество чем PNG!
MERMAID_FORMAT = "svg"  # "svg" или "png"
MERMAID_THEME = "neutral"  # "default", "dark", "forest", "neutral" (рекомендуется neutral для читаемости)
MERMAID_WIDTH = "1200"  # Ширина диаграмм

# Highlight.js темы (для HTML) - https://highlightjs.org/demo
# Популярные тёмные темы:
AVAILABLE_HLJS_THEMES = [
    "github-dark",  # GitHub Dark - отличный выбор!
    "github-dark-dimmed",  # GitHub Dark Dimmed
    "dracula",  # Dracula - популярная тема
    "atom-one-dark",  # Atom One Dark
    "vs2015",  # Visual Studio 2015 Dark
    "monokai",  # Monokai
    "nord",  # Nord
    "tokyo-night-dark",  # Tokyo Night Dark
    "a11y-dark",  # A11y Dark (доступность)
]
HLJS_THEME = "github-dark"  # Для HTML


def postprocess_html_for_mermaid(html_content):
    """
    Восстанавливает символы в Mermaid блоках, которые Pandoc экранировал.
    Pandoc с --embed-resources экранирует --> в --&gt;
    """

    def fix_mermaid_block(match):
        block = match.group(1)
        # Восстанавливаем стрелки и другие символы
        block = block.replace("--&gt;", "-->")
        block = block.replace("&gt;", ">")
        block = block.replace("&lt;", "<")
        block = block.replace("&amp;", "&")
        return f'<pre class="mermaid">{block}</pre>'

    return re.sub(
        r'<pre class="mermaid">(.*?)</pre>',
        fix_mermaid_block,
        html_content,
        flags=re.DOTALL,
    )


# --- ФУНКЦИИ ---


def preprocess_markdown(content, format_type="html"):
    """
    Подготавливает markdown для Pandoc:
    1. Превращает Obsidian Callouts в Pandoc Divs
    2. Удаляет horizontal rules (---) для EPUB
    3. Обрабатывает Mermaid диаграммы для HTML
    """
    # 1. Обработка Obsidian Callouts
    content = re.sub(
        r">\s*\[!(NOTE|INFO|TIP|WARNING|DANGER|ERROR)\]\s*(.*)",
        r"\n::: \1\n**\2**\n",
        content,
        flags=re.IGNORECASE,
    )

    # 2. Удаляем horizontal rules (---) для EPUB - они создают визуальный мусор
    if format_type == "epub":
        # Удаляем строки с ---, ___, *** (тематические разделители)
        content = re.sub(r"^\s*(---|___|\*\*\*)\s*$", "", content, flags=re.MULTILINE)

    # 3. Обработка Mermaid диаграмм - только для HTML
    # Для EPUB Mermaid остается как кодовый блок (требуется mermaid-cli для рендеринга)
    if format_type == "html":

        def replace_mermaid(match):
            mermaid_code = match.group(1)
            # Используем raw HTML блок чтобы Pandoc не трогал содержимое
            # НЕ экранируем - Mermaid нуждается в оригинальных символах
            return f'```{{=html}}\n<pre class="mermaid">\n{mermaid_code}\n</pre>\n```'

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

    return preprocess_markdown(merged_content, format_type)


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
        "--metadata",
        f"title={output_filename}",  # Избавляемся от UNTITLED
    ]

    # Для HTML используем highlight.js (лучше подсвечивает Python)
    # Для EPUB используем Pandoc Skylighting
    if format_type == "html":
        cmd.append("--no-highlight")  # Отключаем Pandoc, используем highlight.js

        # Читаем наш JS файл с улучшениями
        js_file_path = "assets/js/pandoc_enhancements.js"
        with open(js_file_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        # Создаем заголовок с highlight.js и Mermaid
        header_file = os.path.join(OUTPUT_FOLDER, "_header.html")
        with open(header_file, "w", encoding="utf-8") as f:
            f.write(f"""<!-- Highlight.js - {HLJS_THEME} theme -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/{HLJS_THEME}.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>hljs.highlightAll();</script>
<!-- Mermaid -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
<!-- Book Enhancements (Code Copy + Fullscreen) -->
<script>
{js_content}
</script>""")
        cmd.extend(["--include-in-header", header_file])
        cmd.append("--to=html5")
    else:
        # Для EPUB используем кастомную тему подсветки (github-dark)
        # или встроенную тему Pandoc
        if os.path.exists(CUSTOM_THEME_FILE):
            cmd.append(f"--highlight-style={CUSTOM_THEME_FILE}")
            print(f"📎 Используем кастомную тему: {CUSTOM_THEME_FILE}")
        else:
            # Fallback на встроенную тему
            cmd.append("--highlight-style=breezedark")

        cmd.append("--to=epub3")

        # Вшиваем шрифты в EPUB (чтобы PocketBook и др. видели их)
        if EMBED_FONTS_IN_EPUB:
            font_files = [
                os.path.join(FONTS_DIR, f)
                for f in os.listdir(FONTS_DIR)
                if f.endswith((".ttf", ".otf", ".woff", ".woff2"))
            ]
            for font in font_files:
                cmd.extend(["--epub-embed-font", font])
                print(f"📎 Вшиваем шрифт: {os.path.basename(font)}")

        # mermaid-filter рендерит диаграммы в SVG/PNG для EPUB
        # Windows требует mermaid-filter.cmd
        cmd.extend(["-F", "mermaid-filter.cmd"])

    print(f"\nЗапуск Pandoc для {format_type.upper()}...")
    print(f"Команда: {' '.join(cmd)}")

    # Настройки mermaid-filter через переменные окружения
    env = os.environ.copy()
    if format_type == "epub":
        env["MERMAID_FILTER_FORMAT"] = MERMAID_FORMAT  # svg для лучшего качества
        env["MERMAID_FILTER_THEME"] = MERMAID_THEME
        env["MERMAID_FILTER_WIDTH"] = MERMAID_WIDTH
        env["MERMAID_FILTER_BACKGROUND"] = "transparent"
        print(f"🎨 Mermaid: format={MERMAID_FORMAT}, theme={MERMAID_THEME}")

    try:
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, env=env
        )

        # Постобработка HTML для исправления Mermaid
        if format_type == "html":
            with open(output_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            html_content = postprocess_html_for_mermaid(html_content)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            print("✓ Mermaid диаграммы обработаны")

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

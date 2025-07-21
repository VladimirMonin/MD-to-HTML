import markdown
import os
import re
import shutil
import mimetypes
import json
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

# Основные настройки
TEMPLATE = "main.html"
RESULT_FOLDER = "./result"
FILES_FOLDER = r"C:\Syncthing\База Obsidian\9 файлы"
ASSETS_FOLDER = "assets"
BRAND_IMAGE = r"covers\django_logo.jpg"

class DiffPreprocessor(Preprocessor):
    def run(self, lines):
        new_lines = []
        in_diff_block = False
        diff_block_lines = []
        lang = ''

        for line in lines:
            if line.strip().startswith('```diff'):
                in_diff_block = True
                diff_block_lines = []
                # Извлекаем язык, если он указан (например, ```diff-python)
                match = re.match(r'```diff-?(\w+)', line.strip())
                lang = match.group(1) if match else ''
                continue
            elif line.strip() == '```' and in_diff_block:
                in_diff_block = False
                
                before_code = "\n".join([l[1:] for l in diff_block_lines if not l.startswith('+')])
                after_code = "\n".join([l[1:] for l in diff_block_lines if not l.startswith('-')])

                # Экранируем HTML, чтобы он отображался как текст
                before_code_escaped = self._escape(before_code)
                after_code_escaped = self._escape(after_code)
                
                # Передаем язык в класс для highlight.js
                css_class = f'language-{lang}' if lang else ''

                html_structure = f'''
<div class="diff-wrapper">
    <div class="diff-container">
        <div class="diff-header">Было</div>
        <pre><code class="{css_class}">{before_code_escaped}</code></pre>
    </div>
    <div class="diff-container">
        <div class="diff-header">Стало</div>
        <pre><code class="{css_class}">{after_code_escaped}</code></pre>
    </div>
</div>
'''
                placeholder = self.md.htmlStash.store(html_structure)
                new_lines.append(placeholder)
            elif in_diff_block:
                diff_block_lines.append(line)
            else:
                new_lines.append(line)
        
        return new_lines

    def _escape(self, text):
        """Экранирует специальные HTML-символы."""
        return text.replace('&', '&').replace('<', '<').replace('>', '>').replace('"', '"')

class DiffExtension(Extension):
    def extendMarkdown(self, md):
        md.preprocessors.register(DiffPreprocessor(md), 'diff', 27)


def copy_assets(target_dir: str):
    """Копирует assets в папку назначения"""
    target_assets = os.path.join(target_dir, "assets")
    if os.path.exists(ASSETS_FOLDER):
        shutil.copytree(ASSETS_FOLDER, target_assets, dirs_exist_ok=True)
        print(f"Assets скопированы в {target_assets}")
    else:
        print(f"Папка assets не найдена в {os.getcwd()}")


def copy_local_media(md_content: str, media_dir: str, markdown_path: str) -> str:
    """Копирует локальные медиафайлы в папку media и обновляет содержимое Markdown"""
    md_content = re.sub(r"!\[\[(.*?)\]\]", r"![\1](\1)", md_content)
    media_paths = re.findall(r"!\[.*?\]\((?!http)(.*?)\)", md_content)
    media_found = False

    for media_path in media_paths:
        if media_path:
            media_found = True
            os.makedirs(media_dir, exist_ok=True)
            new_path = os.path.join(media_dir, os.path.basename(media_path))

            if os.path.isabs(media_path):
                abs_media_path = media_path
            elif "/" in media_path or "\\" in media_path:
                abs_media_path = os.path.abspath(
                    os.path.join(os.path.dirname(markdown_path), media_path)
                )
            else:
                abs_media_path = os.path.join(FILES_FOLDER, media_path)

            if os.path.exists(abs_media_path):
                shutil.copy(abs_media_path, new_path)
                mime_type, _ = mimetypes.guess_type(new_path)

                if mime_type:
                    if mime_type.startswith("image"):
                        md_content = md_content.replace(
                            media_path, "./media/" + os.path.basename(media_path)
                        )
                    elif mime_type.startswith("audio"):
                        md_content = md_content.replace(
                            f"![{media_path}]({media_path})",
                            f'<audio controls><source src="./media/{os.path.basename(media_path)}" type="{mime_type}">Your browser does not support the audio element.</audio>',
                        )
                    elif mime_type.startswith("video"):
                        md_content = md_content.replace(
                            f"![{media_path}]({media_path})",
                            f'<video controls><source src="./media/{os.path.basename(media_path)}" type="{mime_type}">Your browser does not support the video element.</video>',
                        )
                print(f"Копируется: {media_path} в {new_path}")
            else:
                print(f"Медиафайл не найден: {abs_media_path}")

    if not media_found:
        print("Медиафайлы не найдены в разметке Markdown. Папка media не была создана.")

    return md_content


def read_template(template_path: str) -> str:
    """Читает шаблон HTML из файла"""
    with open(template_path, "r", encoding="utf-8") as file:
        return file.read()


def convert_markdown_to_html(markdown_path: str):
    """Преобразует Markdown в HTML и сохраняет его в файле"""
    base_name = os.path.splitext(os.path.basename(markdown_path))[0]
    target_dir = os.path.join(RESULT_FOLDER, base_name)
    os.makedirs(target_dir, exist_ok=True)

    copy_assets(target_dir)
    media_dir = os.path.join(target_dir, "media")

    if BRAND_IMAGE:
        try:
            brand_filename = os.path.basename(BRAND_IMAGE)
            brand_target_path = os.path.join(target_dir, brand_filename)
            shutil.copy(BRAND_IMAGE, brand_target_path)
            print(f"Обложка скопирована в {brand_target_path}")
            brand_image_relative = "./" + brand_filename
        except Exception as e:
            print(f"Ошибка копирования обложки: {e}")
            brand_image_relative = ""
    else:
        brand_image_relative = ""

    try:
        with open(markdown_path, "r", encoding="utf-8") as file:
            md_content = file.read()

        md_content = copy_local_media(md_content, media_dir, markdown_path)
        
        md_extensions = [
            "extra",
            "tables",
            "fenced_code",
            "pymdownx.superfences",
            DiffExtension(),
        ]

        extension_configs = {
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": lambda source, language, css_class, options, md, **kwargs: f'<pre class="mermaid">{source}</pre>',
                    }
                ]
            }
        }

        html_content = markdown.markdown(
            md_content, extensions=md_extensions, extension_configs=extension_configs
        )
        template = read_template(TEMPLATE)
        html = (
            template.replace("{{ content }}", html_content)
            .replace("{title}", base_name)
            .replace("{header}", base_name)
            .replace("{brand}", brand_image_relative)
        )
        html_path = os.path.join(target_dir, base_name + ".html")

        with open(html_path, "w", encoding="utf-8") as file:
            file.write(html)

        print(f"HTML файл успешно сохранен как {html_path}")
    except FileNotFoundError as e:
        print(
            f"Файл не найден: {e.filename}. Проверьте путь к файлу и попробуйте снова."
        )
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    input_path = (
        input(r"Введите путь к файлу или папке с файлами Markdown: ")
        .replace('"', "")
        .replace("'", "")
        .strip()
    )
    abs_path = os.path.abspath(input_path)
    print(f"Обрабатывается: {abs_path}")
    if os.path.isdir(abs_path):
        md_files = [
            os.path.join(abs_path, f)
            for f in os.listdir(abs_path)
            if os.path.isfile(os.path.join(abs_path, f)) and f.lower().endswith(".md")
        ]
        if md_files:
            for md_file in md_files:
                convert_markdown_to_html(md_file)
        else:
            print("В указанной папке не найдено md файлов.")
    elif os.path.isfile(abs_path) and abs_path.lower().endswith(".md"):
        convert_markdown_to_html(abs_path)
    else:
        print("Неверный путь. Укажите корректный файл или папку с файлами Markdown.")

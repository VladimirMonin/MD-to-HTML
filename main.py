import markdown
import os
import re
import shutil
import mimetypes

# Основные настройки
TEMPLATE = 'main.html'
RESULT_FOLDER = './result'
FILES_FOLDER = r'C:\Syncthing\База Obsidian\9 файлы'
ASSETS_FOLDER = 'assets'

def copy_assets(target_dir: str):
    """Копирует assets в папку назначения"""
    target_assets = os.path.join(target_dir, 'assets')
    if os.path.exists(ASSETS_FOLDER):
        shutil.copytree(ASSETS_FOLDER, target_assets, dirs_exist_ok=True)
        print(f"Assets скопированы в {target_assets}")
    else:
        print(f"Папка assets не найдена в {os.getcwd()}")

def copy_local_media(md_content: str, media_dir: str) -> str:
    """Копирует локальные медиафайлы в папку media и обновляет содержимое Markdown"""
    md_content = re.sub(r'!\[\[(.*?)\]\]', r'![\1](\1)', md_content)
    media_paths = re.findall(r'!\[.*?\]\((?!http)(.*?)\)', md_content)
    media_found = False

    for media_path in media_paths:
        if media_path:
            media_found = True
            os.makedirs(media_dir, exist_ok=True)
            new_path = os.path.join(media_dir, os.path.basename(media_path))
            abs_media_path = os.path.join(FILES_FOLDER, media_path)
            
            if os.path.exists(abs_media_path):
                shutil.copy(abs_media_path, new_path)
                mime_type, _ = mimetypes.guess_type(new_path)

                if mime_type:
                    if mime_type.startswith('image'):
                        md_content = md_content.replace(media_path, './media/' + os.path.basename(media_path))
                    elif mime_type.startswith('audio'):
                        md_content = md_content.replace(
                            f'![{media_path}]({media_path})',
                            f'<audio controls><source src="./media/{os.path.basename(media_path)}" type="{mime_type}">Your browser does not support the audio element.</audio>')
                    elif mime_type.startswith('video'):
                        md_content = md_content.replace(
                            f'![{media_path}]({media_path})',
                            f'<video controls><source src="./media/{os.path.basename(media_path)}" type="{mime_type}">Your browser does not support the video element.</video>')
                print(f"Копируется: {media_path} в {new_path}")
            else:
                print(f"Медиафайл не найден: {abs_media_path}")
    
    if not media_found:
        print("Медиафайлы не найдены в разметке Markdown. Папка media не была создана.")

    return md_content

def read_template(template_path: str) -> str:
    """Читает шаблон HTML из файла"""
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def convert_markdown_to_html(markdown_path: str):
    """Преобразует Markdown в HTML и сохраняет его в файле"""
    base_name = os.path.splitext(os.path.basename(markdown_path))[0]
    target_dir = os.path.join(RESULT_FOLDER, base_name)
    os.makedirs(target_dir, exist_ok=True)

    # Копируем assets в папку результата
    copy_assets(target_dir)
    
    media_dir = os.path.join(target_dir, 'media')

    try:
        with open(markdown_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        md_content = copy_local_media(md_content, media_dir)
        md_extensions = ['extra', 'fenced_code', 'tables']
        html_content = markdown.markdown(md_content, extensions=md_extensions)
        template = read_template(TEMPLATE)
        html = template.replace('{{ content }}', html_content)
        html_path = os.path.join(target_dir, base_name + '.html')

        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(html)

        print(f"HTML файл успешно сохранен как {html_path}")
    except FileNotFoundError as e:
        print(f"Файл не найден: {e.filename}. Проверьте путь к файлу и попробуйте снова.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Запрос пути к файлу от пользователя
markdown_path = input(r"Введите путь к файлу Markdown: ").replace('"', '').replace("'", '')
markdown_path = os.path.abspath(markdown_path)
print(markdown_path)
convert_markdown_to_html(markdown_path)

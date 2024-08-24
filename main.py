import markdown
import os
import re
import shutil
import mimetypes

# Путь к шаблону HTML
TEMPLATE = 'main.html'

# Папка для исходных файлов (определена вами)
FILES_FOLDER = r'C:\Users\user\Syncthing\База Obsidian\9 файлы'


def copy_local_media(md_content: str, media_dir: str) -> str:
    """
    Копирует локальные медиафайлы в папку media и обновляет содержимое Markdown
    :param md_content: Содержимое Markdown
    :param media_dir: Папка для медиафайлов
    """
    # Добавим поддержку для синтаксиса ![[image.png]]
    md_content = re.sub(r'!\[\[(.*?)\]\]', r'![\1](\1)', md_content)

    # Найдем все пути к изображениям, аудио и видео в формате Markdown
    media_paths = re.findall(r'!\[.*?\]\((.*?)\)|\[(.*?)\]\((.*?)\)', md_content)
    
    media_found = False

    for media_path_tuple in media_paths:
        # Путь к медиафайлу
        for media_path in media_path_tuple:
            if media_path and not media_path.startswith('http'):
                media_found = True
                # Создать папку для медиафайлов, если она еще не существует
                os.makedirs(media_dir, exist_ok=True)
                # Определить новый путь для медиафайла
                new_path = os.path.join(media_dir, os.path.basename(media_path))

                # Копировать медиафайл
                abs_media_path = os.path.join(FILES_FOLDER, media_path)
                shutil.copy(abs_media_path, new_path)

                # Определите MIME-тип файла
                mime_type, _ = mimetypes.guess_type(new_path)

                # Определение типа медиафайла и замена в md_content
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
    
    if not media_found:
        print("Медиафайлы не найдены в разметке Markdown. Папка media не была создана.")

    return md_content


def read_template(template_path: str) -> str:
    """Читает шаблон HTML из файла"""
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()


def convert_markdown_to_html(markdown_path: str):
    """
    Преобразует Markdown в HTML и сохраняет его в файле
    :param markdown_path: Путь к файлу Markdown
    """
    # Определение имени файла и создание папки с этим именем
    base_name = os.path.splitext(os.path.basename(markdown_path))[0]
    target_dir = os.path.join(os.getcwd(), base_name)
    os.makedirs(target_dir, exist_ok=True)

    media_dir = os.path.join(target_dir, 'media')

    # Чтение Markdown файла
    try:
        with open(markdown_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        # Обработать локальные медиафайлы (изображения, аудио, видео)
        md_content = copy_local_media(md_content, media_dir)

        # Включение расширений для улучшенной обработки
        md_extensions = ['extra', 'fenced_code', 'tables']

        # Преобразование Markdown в HTML с расширениями
        html_content = markdown.markdown(md_content, extensions=md_extensions)

        # Чтение шаблона
        template = read_template(TEMPLATE)
       
        html = template.replace('{{ content }}', html_content)

        # Определение пути для сохранения HTML файла внутри целевой папки
        html_path = os.path.join(target_dir, base_name + '.html')

        # Сохранение HTML файла
        with open(html_path, 'w', encoding='utf-8') as file:
            file.write(html)

        print(f"HTML файл успешно сохранен как {html_path}")
    except FileNotFoundError:
        print("Файл не найден. Проверьте путь к файлу и попробуйте снова.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


# Запрос пути к файлу от пользователя
markdown_path = input("Введите путь к файлу Markdown: ").replace('"', '').replace("'", '')
convert_markdown_to_html(markdown_path)


import markdown
import os
import re
import shutil

TEMPLATE = 'main.html'

def copy_local_images(md_content: str, images_dir: str) -> str:
    """
    Копирует локальные изображения в папку images и обновляет содержимое Markdown
    :param md_content: Содержимое Markdown
    :param images_dir: Папка для изображений
    """
    image_paths = re.findall(r'!\[.*?\]\((.*?)\)', md_content)
    for image_path in image_paths:
        if not image_path.startswith('http'):
            # Создать папку для изображений, если она еще не существует
            os.makedirs(images_dir, exist_ok=True)
            # Определить новый путь для изображения
            new_path = os.path.join(images_dir, os.path.basename(image_path))
            # Копировать изображение
            shutil.copy(image_path, new_path)
            # Обновить содержимое Markdown
            md_content = md_content.replace(image_path, new_path)
    return md_content

def read_template(template_path: str) -> str:
    """
    Читает шаблон HTML из файла
    :param template_path: Путь к файлу шаблона
    :return: Содержимое шаблона
    """
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def convert_markdown_to_html(markdown_path: str):
    """
    Преобразует Markdown в HTML и сохраняет его в файле
    :param markdown_path: Путь к файлу Markdown
    """
    images_dir = os.path.join(os.path.dirname(markdown_path), 'images')

    # Чтение Markdown файла
    try:
        with open(markdown_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        # Обработать локальные изображения
        md_content = copy_local_images(md_content, images_dir)

        # Включение расширений для улучшенной обработки
        md_extensions = ['extra', 'fenced_code', 'tables']

        # Преобразование Markdown в HTML с расширениями
        html_content = markdown.markdown(md_content, extensions=md_extensions)

        # Чтение шаблона
        template = read_template(TEMPLATE)
       
        html = template.replace('{{ content }}', html_content)

        # Определение пути для сохранения HTML файла
        base = os.path.splitext(markdown_path)[0]
        html_path = base + '.html'

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

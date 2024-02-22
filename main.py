import markdown
import os
import re
import shutil

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

        # Создание HTML-структуры с Bootstrap 5
        html = f"""<!doctype html>
<html lang="ru">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Markdown Converted Document</title>
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Highlight.js Stylesheet -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/styles/tomorrow-night-bright.min.css">
  </head>
  <body>
    <div class="container mt-5">
        {html_content}
    </div>
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Highlight.js Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.3.1/highlight.min.js"></script>
    <!-- Initialization of Highlight.js -->
    <script>hljs.highlightAll();</script>
    <!-- Making images responsive -->
    <script>
      document.addEventListener("DOMContentLoaded", function() {{
        // Adding Bootstrap 'img-fluid' class to all images
        document.querySelectorAll('img').forEach(function(img) {{
          img.classList.add('img-fluid');
        }});
        // Adding Bootstrap 'table' and 'table-striped' classes to all tables
        document.querySelectorAll('table').forEach(function(table) {{
          table.classList.add('table', 'table-striped');
        }});
      }});
    </script>
  </body>
</html>"""

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

import os
import subprocess

# Путь к файлу для тестирования
test_file = (
    r"C:\PY\django_6_blog\doc\architecture\phase_2\13_html_processors_architecture.md"
)

# Проверяем существование файла
if not os.path.exists(test_file):
    print(f"❌ Файл не найден: {test_file}")
    exit(1)

# Импортируем и запускаем функцию напрямую
from build_book import build_book

output_name = "13_html_processors_architecture"
print(f"Запускаем сборку для файла: {test_file}")
print(f"Имя выходного файла: {output_name}")

try:
    print("\n=== Сборка HTML ===")
    build_book(test_file, output_name, "html")

    print("\n=== Сборка EPUB ===")
    build_book(test_file, output_name, "epub")

    print("\n✅ Тест завершен успешно! Созданы файлы:")
    print(f"  - ./build/{output_name}.html")
    print(f"  - ./build/{output_name}.epub")
except Exception as e:
    print(f"\n❌ Ошибка при сборке: {e}")
    import traceback

    traceback.print_exc()

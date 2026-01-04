#!/usr/bin/env python3
"""
MCP Server для MD-to-HTML конвертера.
Предоставляет единый высокоуровневый инструмент для конвертации Markdown в HTML.
"""

import re
import sys
from pathlib import Path
from typing import Optional
from urllib.parse import unquote

# Импорт FastMCP для создания MCP сервера
from mcp.server.fastmcp import FastMCP

# Импорт локальных модулей конвертера
from md_converter import Converter, ConverterConfig
from md_converter.config import (
    InputConfig, 
    FeaturesConfig, 
    StylesConfig, 
    MetadataConfig, 
    FontsConfig, 
    AdvancedConfig
)


# Пользовательские исключения для детальной диагностики
class ValidationError(Exception):
    """Базовая ошибка валидации параметров."""
    pass


class InputFileNotFoundError(ValidationError):
    """Входной Markdown файл не найден."""
    pass


class MediaFolderNotFoundError(ValidationError):
    """Папка с медиа файлами не найдена."""
    pass


class OutputPathNotFoundError(ValidationError):
    """Выходной путь не существует."""
    pass


class MediaFilesNotFoundError(ValidationError):
    """Некоторые медиа файлы, упомянутые в документе, не найдены."""
    
    def __init__(self, missing_files: list[str]):
        self.missing_files = missing_files
        super().__init__(
            f"Следующие медиа файлы не найдены ({len(missing_files)}): "
            f"{', '.join(missing_files[:5])}"
            + (f" и еще {len(missing_files) - 5}" if len(missing_files) > 5 else "")
        )


# Инициализация MCP сервера
mcp = FastMCP(
    "MD-to-HTML Converter",
    website_url="https://github.com/VladimirMonin/MD-to-HTML"
)


def extract_media_paths(markdown_content: str) -> list[str]:
    """
    Извлечь все пути к медиа файлам из Markdown контента.
    
    Args:
        markdown_content: Содержимое Markdown файла
        
    Returns:
        Список путей к медиа файлам (без HTTP/HTTPS URL)
    """
    # Регулярное выражение для поиска ссылок на изображения/медиа
    media_paths = re.findall(r"!\[.*?\]\((?!http)(.*?)\)", markdown_content)
    
    # URL-декодирование путей (для "Pasted%20image%20..." и т.д.)
    decoded_paths = [unquote(path) for path in media_paths if path]
    
    return decoded_paths


def validate_media_files(
    markdown_path: Path,
    media_folder: Path,
    markdown_content: str
) -> list[str]:
    """
    Проверить наличие всех медиа файлов, упомянутых в Markdown документе.
    
    Args:
        markdown_path: Путь к Markdown файлу
        media_folder: Папка с медиа файлами
        markdown_content: Содержимое Markdown файла
        
    Returns:
        Список отсутствующих файлов
    """
    missing_files = []
    media_paths = extract_media_paths(markdown_content)
    
    for media_path in media_paths:
        # Определяем абсолютный путь к медиа файлу
        if Path(media_path).is_absolute():
            abs_path = Path(media_path)
        elif "/" in media_path or "\\" in media_path:
            # Относительный путь от Markdown файла
            abs_path = markdown_path.parent / media_path
        else:
            # Только имя файла - ищем в media_folder
            abs_path = media_folder / media_path
        
        if not abs_path.exists():
            missing_files.append(str(media_path))
    
    return missing_files


@mcp.tool()
def convert_markdown_to_html(
    input_file: str,
    media_folder: str,
    output_path: str,
    enable_toc: bool = True,
    toc_depth: int = 2,
    enable_breadcrumbs: bool = True,
    output_format: str = "html",
    template: str = "web",
    media_mode: str = "embed",
    validate_media: bool = True,
    mermaid_theme: str = "forest"
) -> dict:
    """
    Конвертирует Markdown файл в HTML с проверкой всех зависимостей.
    
    Этот инструмент выполняет полную конвертацию Markdown документа в HTML формат
    с поддержкой:
    - Встраивания изображений и медиа файлов
    - Генерации оглавления (TOC) с настраиваемой глубиной
    - Хлебных крошек для навигации
    - Подсветки синтаксиса кода
    - Diff блоков
    - Callouts (специальные блоки внимания)
    - Mermaid диаграмм
    - Plyr медиаплеера
    
    ОБЯЗАТЕЛЬНЫЕ ПАРАМЕТРЫ:
    
    input_file (str): Абсолютный путь к входному Markdown файлу.
        Примеры: 
        - "C:/docs/lesson.md"
        - "/home/user/documents/readme.md"
        Проверка: файл должен существовать и иметь расширение .md
        
    media_folder (str): Абсолютный путь к папке с медиа файлами (изображения, видео, аудио).
        Примеры:
        - "C:/docs/media"
        - "/home/user/documents/images"
        Проверка: папка должна существовать
        
    output_path (str): Абсолютный путь к директории для сохранения результата.
        Примеры:
        - "C:/docs/output"
        - "/home/user/documents/results"
        Проверка: директория должна существовать (или будет создана)
        
    ОПЦИОНАЛЬНЫЕ ПАРАМЕТРЫ:
    
    enable_toc (bool): Включить генерацию оглавления (Table of Contents).
        По умолчанию: True
        Создает навигационное меню на основе заголовков документа.
        
    toc_depth (int): Глубина оглавления (уровни заголовков от 1 до 6).
        По умолчанию: 2 (H1 и H2)
        Примеры:
        - 1: только H1
        - 3: H1, H2, H3
        - 6: все уровни заголовков
        
    enable_breadcrumbs (bool): Включить хлебные крошки навигации.
        По умолчанию: True
        Добавляет навигационную цепочку в верхней части страницы.
        
    output_format (str): Формат выходного файла.
        По умолчанию: "html"
        Поддерживаемые значения: "html", "epub"
        
    template (str): Тип шаблона оформления.
        По умолчанию: "web"
        Варианты:
        - "web": современный веб-дизайн с адаптивной версткой
        - "book": стиль электронной книги
        
    media_mode (str): Режим обработки медиа файлов.
        По умолчанию: "embed"
        Варианты:
        - "embed": встраивание медиа в HTML (base64)
        - "copy": копирование медиа файлов рядом с HTML
        
    validate_media (bool): Проверять наличие всех медиа файлов перед конвертацией.
        По умолчанию: True
        Если True, конвертация не начнется, если какие-то медиа файлы отсутствуют.
        
    mermaid_theme (str): Тема для Mermaid диаграмм.
        По умолчанию: "forest" (зелёная)
        Варианты: "default", "forest", "dark", "neutral", "base"
        
    ПРОВЕРКИ И ВАЛИДАЦИЯ:
    
    Инструмент выполняет следующие проверки перед конвертацией:
    
    1. Проверка входного файла:
       - Файл существует
       - Файл имеет расширение .md
       - Файл читаем
       Исключение: InputFileNotFoundError
       
    2. Проверка папки медиа:
       - Папка существует
       - Папка доступна для чтения
       Исключение: MediaFolderNotFoundError
       
    3. Проверка выходного пути:
       - Родительская директория существует
       - Директория доступна для записи
       Исключение: OutputPathNotFoundError
       
    4. Проверка медиа файлов (если validate_media=True):
       - Парсинг Markdown для поиска ссылок на медиа
       - Проверка существования каждого медиа файла
       - Поддержка абсолютных и относительных путей
       - URL-декодирование путей (для "Pasted%20image%20...")
       Исключение: MediaFilesNotFoundError с списком отсутствующих файлов
       
    ВОЗВРАЩАЕМОЕ ЗНАЧЕНИЕ:
    
    dict: Словарь с результатами конвертации:
        {
            "status": "success",
            "output_files": [
                "/absolute/path/to/output.html"
            ],
            "stats": {
                "input_file": "/path/to/input.md",
                "file_size": 12345,  # байт
                "media_files_found": 5,
                "media_files_missing": 0,
                "output_format": "html"
            },
            "message": "Конвертация успешно завершена"
        }
        
    ОБРАБОТКА ОШИБОК:
    
    При возникновении ошибок возвращается dict с детальной информацией:
    
    1. InputFileNotFoundError:
        {
            "status": "error",
            "error_type": "InputFileNotFoundError",
            "message": "Входной файл не найден: /path/to/file.md",
            "details": {
                "input_file": "/path/to/file.md",
                "exists": false
            }
        }
        
    2. MediaFolderNotFoundError:
        {
            "status": "error",
            "error_type": "MediaFolderNotFoundError",
            "message": "Папка медиа не найдена: /path/to/media",
            "details": {
                "media_folder": "/path/to/media",
                "exists": false
            }
        }
        
    3. OutputPathNotFoundError:
        {
            "status": "error",
            "error_type": "OutputPathNotFoundError",
            "message": "Выходной путь не существует: /path/to/output",
            "details": {
                "output_path": "/path/to/output",
                "exists": false
            }
        }
        
    4. MediaFilesNotFoundError:
        {
            "status": "error",
            "error_type": "MediaFilesNotFoundError",
            "message": "Некоторые медиа файлы не найдены",
            "details": {
                "missing_files": [
                    "images/diagram.png",
                    "media/video.mp4",
                    "Pasted image 20230515123045.png"
                ],
                "total_missing": 3,
                "media_folder": "/path/to/media"
            }
        }
        
    5. Общие ошибки:
        {
            "status": "error",
            "error_type": "Exception",
            "message": "Описание ошибки",
            "details": {
                "traceback": "..."  # Если доступен
            }
        }
    
    ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
    
    Минимальный вызов (все опции по умолчанию):
    ```python
    result = convert_markdown_to_html(
        input_file="C:/docs/lesson.md",
        media_folder="C:/docs/media",
        output_path="C:/docs/output"
    )
    ```
    
    Полный вызов с настройками:
    ```python
    result = convert_markdown_to_html(
        input_file="/home/user/documents/tutorial.md",
        media_folder="/home/user/documents/images",
        output_path="/home/user/documents/html",
        enable_toc=True,
        toc_depth=3,
        enable_breadcrumbs=True,
        output_format="html",
        template="web",
        media_mode="embed",
        validate_media=True
    )
    ```
    
    Конвертация без проверки медиа (быстрее, но рискованнее):
    ```python
    result = convert_markdown_to_html(
        input_file="C:/docs/draft.md",
        media_folder="C:/docs/media",
        output_path="C:/docs/output",
        validate_media=False
    )
    ```
    
    Создание EPUB книги:
    ```python
    result = convert_markdown_to_html(
        input_file="C:/books/chapter1.md",
        media_folder="C:/books/media",
        output_path="C:/books/output",
        output_format="epub",
        template="book",
        toc_depth=4
    )
    ```
    """
    try:
        # ===== ЭТАП 1: ВАЛИДАЦИЯ ВХОДНЫХ ПАРАМЕТРОВ =====
        
        # Проверка входного файла
        input_path = Path(input_file)
        if not input_path.exists():
            raise InputFileNotFoundError(
                f"Входной файл не найден: {input_file}"
            )
        
        if not input_path.is_file():
            raise InputFileNotFoundError(
                f"Указанный путь не является файлом: {input_file}"
            )
            
        if input_path.suffix.lower() != ".md":
            raise ValidationError(
                f"Входной файл должен иметь расширение .md, получено: {input_path.suffix}"
            )
        
        # Проверка папки медиа
        media_path = Path(media_folder)
        if not media_path.exists():
            raise MediaFolderNotFoundError(
                f"Папка медиа не найдена: {media_folder}"
            )
        
        if not media_path.is_dir():
            raise MediaFolderNotFoundError(
                f"Указанный путь не является директорией: {media_folder}"
            )
        
        # Проверка выходного пути (создаем если не существует)
        output_dir = Path(output_path)
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise OutputPathNotFoundError(
                    f"Не удалось создать выходную директорию {output_path}: {e}"
                )
        
        # ===== ЭТАП 2: ПРОВЕРКА МЕДИА ФАЙЛОВ =====
        
        markdown_content = input_path.read_text(encoding="utf-8")
        missing_files = []
        
        if validate_media:
            missing_files = validate_media_files(
                input_path,
                media_path,
                markdown_content
            )
            
            if missing_files:
                raise MediaFilesNotFoundError(missing_files)
        
        # ===== ЭТАП 3: ПОДГОТОВКА КОНФИГУРАЦИИ =====
        
        config = ConverterConfig(
            output_dir=str(output_dir),
            template=template,
            media_mode=media_mode,
            formats=[output_format],
            input=InputConfig(
                path=str(input_path),
                source_type="standard",
                files_folder=str(media_path)
            ),
            metadata=MetadataConfig(
                title="",
                author="",
                lang="ru",
                brand_image=""mermaid_theme
            ),
            styles=StylesConfig(
                highlight_theme="github-dark",
                mermaid_theme="neutral"
            ),
            fonts=FontsConfig(
                embed=True,
                dir="assets/fonts"
            ),
            features=FeaturesConfig(
                toc=enable_toc,
                toc_depth=toc_depth,
                breadcrumbs=enable_breadcrumbs,
                code_copy=True,
                fullscreen=True,
                diff_blocks=True,
                callouts=True,
                mermaid=True,
                plyr=True
            ),
            advanced=AdvancedConfig(
                pandoc_extra_args=[],
                custom_css=[],
                custom_js=[]
            )
        )
        
        # ===== ЭТАП 4: КОНВЕРТАЦИЯ =====
        
        converter = Converter(config)
        output_files = converter.convert(input_path)
        
        # ===== ЭТАП 5: ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====
        
        return {
            "status": "success",
            "output_files": [str(f) for f in output_files],
            "stats": {
                "input_file": str(input_path),
                "file_size": input_path.stat().st_size,
                "media_files_found": len(extract_media_paths(markdown_content)),
                "media_files_missing": len(missing_files),
                "output_format": output_format
            },
            "message": "Конвертация успешно завершена"
        }
        
    except InputFileNotFoundError as e:
        return {
            "status": "error",
            "error_type": "InputFileNotFoundError",
            "message": str(e),
            "details": {
                "input_file": input_file,
                "exists": Path(input_file).exists()
            }
        }
        
    except MediaFolderNotFoundError as e:
        return {
            "status": "error",
            "error_type": "MediaFolderNotFoundError",
            "message": str(e),
            "details": {
                "media_folder": media_folder,
                "exists": Path(media_folder).exists()
            }
        }
        
    except OutputPathNotFoundError as e:
        return {
            "status": "error",
            "error_type": "OutputPathNotFoundError",
            "message": str(e),
            "details": {
                "output_path": output_path,
                "exists": Path(output_path).exists()
            }
        }
        
    except MediaFilesNotFoundError as e:
        return {
            "status": "error",
            "error_type": "MediaFilesNotFoundError",
            "message": str(e),
            "details": {
                "missing_files": e.missing_files,
                "total_missing": len(e.missing_files),
                "media_folder": media_folder
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
            "details": {
                "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else None
            }
        }


if __name__ == "__main__":
    # Запуск MCP сервера с stdio транспортом (по умолчанию)
    mcp.run()

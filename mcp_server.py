#!/usr/bin/env python3
"""
MCP Server для MD-to-HTML конвертера.
Предоставляет единый высокоуровневый инструмент для конвертации Markdown в HTML.
"""

import io
import logging
import re
import subprocess
import sys
from contextlib import redirect_stdout
from datetime import datetime
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import unquote

# Настройка файлового логирования для диагностики
LOG_FILE = Path(__file__).parent / "mcp_debug.log"
file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger("mcp_server")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.propagate = False  # Не передавать в root logger


def log_debug(message: str):
    """Логирование в файл и stderr."""
    logger.debug(message)
    print(f"[MCP] {message}", file=sys.stderr)


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
    AdvancedConfig,
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


class MermaidValidationError(ValidationError):
    """Ошибки валидации Mermaid диаграмм."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        error_details = "\n".join(
            [
                f"  • Диаграмма #{err['index']}: {err['error']}\n"
                f"    Код:\n{err['code'][:100]}..."
                for err in errors[:3]
            ]
        )
        super().__init__(
            f"Обнаружены ошибки в {len(errors)} Mermaid диаграммах:\n{error_details}"
            + (f"\n  ... и еще {len(errors) - 3} ошибок" if len(errors) > 3 else "")
        )


# Инициализация MCP сервера
mcp = FastMCP(
    "MD-to-HTML Converter", website_url="https://github.com/VladimirMonin/MD-to-HTML"
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
    markdown_path: Path, media_folder: Path, markdown_content: str
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


def find_mmdc_executable() -> str:
    """
    Найти исполняемый файл mmdc с учетом специфики разных платформ.

    На Windows npm глобальные пакеты устанавливаются в AppData/Roaming/npm,
    и subprocess может не видеть их через PATH если процесс запущен до установки.

    Returns:
        Путь к mmdc исполняемому файлу

    Raises:
        FileNotFoundError: Если mmdc не найден
    """
    import shutil
    import os
    import sys

    # Попытка 1: Через shutil.which (работает если mmdc в PATH)
    mmdc = shutil.which("mmdc")
    if mmdc:
        return mmdc

    # Попытка 2: Windows - проверяем стандартное расположение npm глобальных пакетов
    if sys.platform == "win32":
        npm_global = os.path.expanduser(r"~\AppData\Roaming\npm")

        # Windows использует .cmd обертку для Node.js скриптов
        for variant in ["mmdc.cmd", "mmdc"]:
            mmdc_path = os.path.join(npm_global, variant)
            if os.path.exists(mmdc_path):
                return mmdc_path

    # Попытка 3: Unix - проверяем стандартные npm пути
    else:
        for npm_prefix in [
            "/usr/local/bin",
            os.path.expanduser("~/.npm-global/bin"),
            "/usr/bin",
        ]:
            mmdc_path = os.path.join(npm_prefix, "mmdc")
            if os.path.exists(mmdc_path):
                return mmdc_path

    # Не найден нигде
    raise FileNotFoundError(
        "Mermaid CLI (mmdc) не найден. Установите: npm install -g @mermaid-js/mermaid-cli\n"
        "После установки может потребоваться перезапуск терминала/IDE для обновления PATH."
    )


def validate_mermaid_blocks(markdown_content: str) -> list[dict]:
    """
    Валидация всех Mermaid диаграмм в документе через CLI.

    Проверяет синтаксис каждой диаграммы запуском mmdc в тестовом режиме.
    Возвращает детальные отчеты об ошибках для каждой проблемной диаграммы.

    Args:
        markdown_content: Содержимое Markdown файла

    Returns:
        Список словарей с информацией об ошибках:
        [
            {
                'index': 1,  # Номер диаграммы в документе
                'code': '...',  # Первые 150 символов кода диаграммы
                'error': 'Parse error on line 3...',  # Текст ошибки из CLI
                'line': 45  # Строка в исходном документе (если определена)
            },
            ...
        ]
    """
    import subprocess
    import tempfile
    from pathlib import Path

    # Находим mmdc с учетом специфики платформы
    try:
        mmdc_cmd = find_mmdc_executable()
    except FileNotFoundError as e:
        # Возвращаем специальную ошибку если mmdc не установлен
        return [{"index": 0, "code": "", "error": str(e), "line": 0}]

    errors = []

    # Извлекаем все Mermaid блоки с их позициями
    pattern = r"```mermaid\s*\n(.*?)```"
    matches = list(re.finditer(pattern, markdown_content, re.DOTALL))

    if not matches:
        return []  # Нет диаграмм - нет проблем

    total = len(matches)
    log_debug(f"Валидация {total} Mermaid диаграмм...")

    # Проверяем каждую диаграмму
    for idx, match in enumerate(matches, start=1):
        log_debug(f"Валидация диаграммы {idx}/{total}...")
        diagram_code = match.group(1).strip()

        # Определяем номер строки в документе
        line_number = markdown_content[: match.start()].count("\n") + 1

        # Создаем временный файл для диаграммы
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(diagram_code)
            tmp_path = Path(tmp_file.name)

        try:
            # Пытаемся рендерить в SVG (легковесный формат для теста)
            output_path = tmp_path.with_suffix(".svg")

            result = subprocess.run(
                [
                    mmdc_cmd,
                    "-i",
                    str(tmp_path),
                    "-o",
                    str(output_path),
                    "-t",
                    "neutral",  # Базовая тема для теста
                ],
                capture_output=True,
                text=True,
                timeout=10,  # 10 секунд на диаграмму
                stdin=subprocess.DEVNULL,  # Не блокировать MCP stdio
            )

            # Если процесс завершился с ошибкой
            if result.returncode != 0:
                # Извлекаем суть ошибки из stderr
                error_msg = result.stderr.strip()

                # Упрощаем сообщение (убираем технические детали CLI)
                if "Parse error" in error_msg:
                    # Оставляем только суть синтаксической ошибки
                    error_lines = [
                        l
                        for l in error_msg.split("\n")
                        if "Parse error" in l or "Expecting" in l
                    ]
                    error_msg = " ".join(error_lines[:2]) if error_lines else error_msg
                elif "Error" in error_msg:
                    # Берем первую строку с "Error"
                    error_lines = [l for l in error_msg.split("\n") if "Error" in l]
                    error_msg = error_lines[0] if error_lines else error_msg

                # Обрезаем слишком длинные сообщения
                if len(error_msg) > 200:
                    error_msg = error_msg[:197] + "..."

                errors.append(
                    {
                        "index": idx,
                        "code": diagram_code[:150]
                        + ("..." if len(diagram_code) > 150 else ""),
                        "error": error_msg or "Неизвестная ошибка синтаксиса",
                        "line": line_number,
                    }
                )

            # Удаляем временные файлы
            if output_path.exists():
                output_path.unlink()

        except subprocess.TimeoutExpired:
            errors.append(
                {
                    "index": idx,
                    "code": diagram_code[:150]
                    + ("..." if len(diagram_code) > 150 else ""),
                    "error": "Timeout: диаграмма слишком сложная или зациклена",
                    "line": line_number,
                }
            )
        finally:
            # Удаляем входной временный файл
            if tmp_path.exists():
                tmp_path.unlink()

    return errors


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
    validate_mermaid: bool = False,  # ОТКЛЮЧЕНО - двойная обработка Mermaid
    mermaid_theme: str = "forest",
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

    validate_mermaid (bool): Проверять синтаксис Mermaid диаграмм через CLI перед конвертацией.
        По умолчанию: True
        Если True, конвертация не начнется при наличии синтаксических ошибок в диаграммах.
        Требует установленного Mermaid CLI (mmdc).

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
            raise InputFileNotFoundError(f"Входной файл не найден: {input_file}")

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
            raise MediaFolderNotFoundError(f"Папка медиа не найдена: {media_folder}")

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
                input_path, media_path, markdown_content
            )

            if missing_files:
                raise MediaFilesNotFoundError(missing_files)

        # ===== ЭТАП 2.5: ВАЛИДАЦИЯ MERMAID ДИАГРАММ =====

        if validate_mermaid:
            mermaid_errors = validate_mermaid_blocks(markdown_content)

            if mermaid_errors:
                raise MermaidValidationError(mermaid_errors)

        # ===== ЭТАП 3: ПОДГОТОВКА КОНФИГУРАЦИИ =====

        config = ConverterConfig(
            output_dir=str(output_dir),
            template=template if template in ("book", "web") else "web",  # type: ignore[arg-type]
            media_mode=media_mode if media_mode in ("embed", "copy") else "embed",  # type: ignore[arg-type]
            formats=[output_format],
            input=InputConfig(
                path=str(input_path),
                source_type="standard",
                files_folder=str(media_path),
            ),
            metadata=MetadataConfig(title="", author="", lang="ru", brand_image=""),
            styles=StylesConfig(
                highlight_theme="github-dark", mermaid_theme=mermaid_theme
            ),
            fonts=FontsConfig(embed=True, dir="assets/fonts"),
            features=FeaturesConfig(
                toc=enable_toc,
                toc_depth=toc_depth,
                breadcrumbs=enable_breadcrumbs,
                code_copy=True,
                fullscreen=True,
                diff_blocks=True,
                callouts=True,
                mermaid=True,
                plyr=True,
            ),
            advanced=AdvancedConfig(pandoc_extra_args=[], custom_css=[], custom_js=[]),
        )

        # ===== ЭТАП 4: КОНВЕРТАЦИЯ =====

        log_debug(f"Начинаю конвертацию: {input_path}")
        log_debug(f"Режим медиа: {media_mode}, Формат: {output_format}")

        # Создаём конвертер
        converter = Converter(config)

        # redirect_stdout УДАЛЁН - он не ловит subprocess (Pandoc/mmdc)
        # и потенциально опасен для MCP stdio транспорта
        output_files = converter.convert(input_path)

        log_debug(f"Конвертация завершена, создано файлов: {len(output_files)}")

        # ===== ЭТАП 5: ФОРМИРОВАНИЕ РЕЗУЛЬТАТА =====

        result = {
            "status": "success",
            "output_files": [str(f) for f in output_files],
            "stats": {
                "input_file": str(input_path),
                "file_size": input_path.stat().st_size,
                "media_files_found": len(extract_media_paths(markdown_content)),
                "media_files_missing": len(missing_files),
                "output_format": output_format,
            },
            "message": "Конвертация успешно завершена",
        }

        # Логирование для отладки
        log_debug(f"OK Завершено успешно")
        log_debug(f"FILES Создано файлов: {len(result['output_files'])}")
        log_debug(
            f"MEDIA {result['stats']['media_files_found']} найдено, {result['stats']['media_files_missing']} отсутствует"
        )

        return result

    except InputFileNotFoundError as e:
        return {
            "status": "error",
            "error_type": "InputFileNotFoundError",
            "message": str(e),
            "details": {"input_file": input_file, "exists": Path(input_file).exists()},
        }

    except MediaFolderNotFoundError as e:
        return {
            "status": "error",
            "error_type": "MediaFolderNotFoundError",
            "message": str(e),
            "details": {
                "media_folder": media_folder,
                "exists": Path(media_folder).exists(),
            },
        }

    except OutputPathNotFoundError as e:
        return {
            "status": "error",
            "error_type": "OutputPathNotFoundError",
            "message": str(e),
            "details": {
                "output_path": output_path,
                "exists": Path(output_path).exists(),
            },
        }

    except MediaFilesNotFoundError as e:
        return {
            "status": "error",
            "error_type": "MediaFilesNotFoundError",
            "message": str(e),
            "details": {
                "missing_files": e.missing_files,
                "total_missing": len(e.missing_files),
                "media_folder": media_folder,
            },
        }

    except Exception as e:
        import traceback

        tb_str = traceback.format_exc()
        log_debug(f"ОШИБКА: {type(e).__name__}: {e}\n{tb_str}")
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": str(e),
            "details": {"traceback": tb_str},
        }


if __name__ == "__main__":
    # Запуск MCP сервера с stdio транспортом (по умолчанию)
    mcp.run()

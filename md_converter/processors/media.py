"""Процессор для обработки медиа файлов (из main.py)."""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Tuple


class MediaProcessor:
    """
    Обрабатывает медиа файлы:
    - Режим EMBED: оставляет пути как есть (Pandoc встроит)
    - Режим COPY: копирует в ./media/, заменяет пути
    """

    def __init__(
        self, mode: str = "embed", files_folder: str = "", output_dir: str = "./build"
    ):
        """
        Args:
            mode: "embed" или "copy"
            files_folder: Папка для поиска медиа (Obsidian vault)
            output_dir: Папка для сохранения результатов (по умолчанию ./build)
        """
        self.mode = mode
        self.files_folder = Path(files_folder) if files_folder else None
        self.output_dir = Path(output_dir)

    def process(self, content: str, input_path: Path) -> Tuple[str, dict]:
        """
        Обработать медиа в Markdown.

        Returns:
            (обработанный_контент, media_map)
        """
        media_map = {}
        media_paths = re.findall(r"!\[.*?\]\((?!http)(.*?)\)", content)

        if not media_paths:
            print("  ℹ️ Медиафайлы не найдены в MD", file=sys.stderr)
            if self.mode == "copy":
                self._copy_assets()
            return content, {}

        print(f"  🔍 Найдено {len(media_paths)} ссылок на медиа", file=sys.stderr)

        # Для COPY режима создаём папку media
        if self.mode == "copy":
            media_dir = self.output_dir / "media"
            media_dir.mkdir(parents=True, exist_ok=True)
            self._copy_assets()

        for media_path in media_paths:
            if not media_path:
                continue

            # URL-декодирование пути (для "Pasted%20image%20...")
            from urllib.parse import unquote

            decoded_path = unquote(media_path)

            # Пропускаем data URI (base64 встроенные изображения/шрифты)
            # Эти ресурсы уже встроены, искать файл не нужно
            if decoded_path.startswith("data:"):
                continue

            # Определяем абсолютный путь к медиа-файлу
            abs_path = None
            search_locations = []  # Для логирования

            if Path(decoded_path).is_absolute():
                # Абсолютный путь - используем напрямую
                abs_path = Path(decoded_path)
                search_locations.append(f"абсолютный путь: {abs_path}")
            elif "/" in decoded_path or "\\" in decoded_path:
                # Относительный путь с подпапками (images/pic.png)
                # Сначала пробуем files_folder (приоритет выше)
                if self.files_folder:
                    candidate = self.files_folder / decoded_path
                    search_locations.append(f"files_folder: {candidate}")
                    if candidate.exists():
                        abs_path = candidate

                # Если не нашли, пробуем относительно MD-файла
                if abs_path is None:
                    candidate = input_path.parent / decoded_path
                    search_locations.append(f"input_path.parent: {candidate}")
                    if candidate.exists():
                        abs_path = candidate
            else:
                # Только имя файла (pic.png) - ищем в files_folder
                if self.files_folder:
                    candidate = self.files_folder / decoded_path
                    search_locations.append(f"files_folder: {candidate}")
                    if candidate.exists():
                        abs_path = candidate

                # Fallback: ищем относительно MD-файла
                if abs_path is None:
                    candidate = input_path.parent / decoded_path
                    search_locations.append(f"input_path.parent: {candidate}")
                    if candidate.exists():
                        abs_path = candidate

            # Обработка найденного файла
            if abs_path and abs_path.exists():
                if self.mode == "copy":
                    # Копируем в media/
                    target_path = media_dir / abs_path.name

                    # Пропускаем если файл уже в целевой директории (созданный MermaidPreprocessor)
                    if abs_path.resolve() == target_path.resolve():
                        print(f"  📎 {abs_path.name} (уже в media/)", file=sys.stderr)
                        new_path = f"media/{abs_path.name}"
                        content = content.replace(media_path, new_path)
                        media_map[media_path] = new_path
                    else:
                        shutil.copy2(abs_path, target_path)
                        new_path = f"media/{abs_path.name}"
                        content = content.replace(media_path, new_path)
                        media_map[media_path] = new_path
                        print(f"  📎 {abs_path.name}", file=sys.stderr)
                        print(f"     ├─ источник: {abs_path}", file=sys.stderr)
                        print(f"     └─ скопирован → {new_path}", file=sys.stderr)
                else:
                    # EMBED режим - заменяем на абсолютный путь для Pandoc
                    # Используем resolve() для нормализации пути (убирает .. и т.д.)
                    normalized_path = str(abs_path.resolve())
                    content = content.replace(media_path, normalized_path)
                    media_map[media_path] = normalized_path
                    print(f"  📎 {abs_path.name}", file=sys.stderr)
                    print(f"     ├─ источник: {abs_path}", file=sys.stderr)
                    print(f"     └─ будет встроен (EMBED)", file=sys.stderr)
            else:
                # Файл не найден - выводим все места поиска
                print(f"  ⚠️ НЕ НАЙДЕН: {decoded_path}", file=sys.stderr)
                print(f"     Искали в:", file=sys.stderr)
                for location in search_locations:
                    print(f"     - {location}", file=sys.stderr)

        return content, media_map

    def _copy_assets(self):
        """Копирование assets (CSS/JS/fonts) в output_dir для режима copy."""
        # Получаем абсолютный путь к папке assets от корня проекта
        project_root = Path(__file__).parent.parent.parent
        assets_src = project_root / "assets"

        if not assets_src.exists():
            print(f"⚠️ Папка assets не найдена: {assets_src}", file=sys.stderr)
            return

        assets_dest = self.output_dir / "assets"

        # ИСПРАВЛЕНИЕ БАГ #10: Копируем ВСЕ CSS рекурсивно (включая modules/)
        css_src = assets_src / "css"
        if css_src.exists():
            css_dest = assets_dest / "css"
            css_dest.mkdir(parents=True, exist_ok=True)
            for css_file in css_src.rglob("*.css"):
                rel_path = css_file.relative_to(css_src)
                dest_file = css_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(css_file, dest_file)
            print("  📁 Скопированы CSS файлы (включая модули)", file=sys.stderr)

        # Копируем JS
        js_src = assets_src / "js"
        if js_src.exists():
            js_dest = assets_dest / "js"
            js_dest.mkdir(parents=True, exist_ok=True)
            for js_file in js_src.rglob("*.js"):
                rel_path = js_file.relative_to(js_src)
                dest_file = js_dest / rel_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(js_file, dest_file)
            print(f"  📁 Скопированы JS файлы", file=sys.stderr)

        # Копируем шрифты
        fonts_src = assets_src / "fonts"
        if fonts_src.exists():
            fonts_dest = assets_dest / "fonts"
            fonts_dest.mkdir(parents=True, exist_ok=True)
            for font_file in fonts_src.glob("*"):
                if font_file.is_file():
                    shutil.copy2(font_file, fonts_dest / font_file.name)
            print(f"  📁 Скопированы шрифты", file=sys.stderr)

        # Копируем templates (если нужны)
        templates_src = assets_src / "templates"
        if templates_src.exists():
            templates_dest = assets_dest / "templates"
            templates_dest.mkdir(parents=True, exist_ok=True)
            for template_file in templates_src.glob("*.html"):
                shutil.copy2(template_file, templates_dest / template_file.name)
            print(f"  📁 Скопированы HTML шаблоны", file=sys.stderr)

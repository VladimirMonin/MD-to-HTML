"""Процессор для обработки медиа файлов (из main.py)."""

import os
import re
import shutil
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
            print("  ℹ️ Медиафайлы не найдены в MD")
            if self.mode == "copy":
                self._copy_assets()
            return content, {}

        print(f"  🔍 Найдено {len(media_paths)} ссылок на медиа")

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

            # Определяем абсолютный путь
            if Path(decoded_path).is_absolute():
                abs_path = Path(decoded_path)
            elif "/" in decoded_path or "\\" in decoded_path:
                # Относительный путь
                abs_path = input_path.parent / decoded_path
            else:
                # Только имя файла — ищем в files_folder
                if self.files_folder:
                    abs_path = self.files_folder / decoded_path
                else:
                    abs_path = input_path.parent / decoded_path

            if abs_path.exists():
                if self.mode == "copy":
                    # Копируем в media/
                    target_path = media_dir / abs_path.name
                    shutil.copy2(abs_path, target_path)
                    new_path = f"media/{abs_path.name}"
                    content = content.replace(media_path, new_path)
                    media_map[media_path] = new_path
                    print(f"  📎 {abs_path.name} → скопирован в {new_path}")
                else:
                    # EMBED режим - заменяем на абсолютный путь для Pandoc
                    content = content.replace(media_path, str(abs_path))
                    media_map[media_path] = str(abs_path)
                    print(f"  📎 {abs_path.name} → будет встроен (EMBED)")
            else:
                print(f"  ⚠️ Не найден: {decoded_path}")

        return content, media_map

    def _copy_assets(self):
        """Копирование assets (CSS/JS/fonts) в output_dir для режима copy."""
        assets_src = Path("assets")
        if not assets_src.exists():
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
            print("  📁 Скопированы CSS файлы (включая модули)")

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
            print(f"  📁 Скопированы JS файлы")

        # Копируем шрифты
        fonts_src = assets_src / "fonts"
        if fonts_src.exists():
            fonts_dest = assets_dest / "fonts"
            fonts_dest.mkdir(parents=True, exist_ok=True)
            for font_file in fonts_src.glob("*"):
                if font_file.is_file():
                    shutil.copy2(font_file, fonts_dest / font_file.name)
            print(f"  📁 Скопированы шрифты")

        # Копируем templates (если нужны)
        templates_src = assets_src / "templates"
        if templates_src.exists():
            templates_dest = assets_dest / "templates"
            templates_dest.mkdir(parents=True, exist_ok=True)
            for template_file in templates_src.glob("*.html"):
                shutil.copy2(template_file, templates_dest / template_file.name)
            print(f"  📁 Скопированы HTML шаблоны")

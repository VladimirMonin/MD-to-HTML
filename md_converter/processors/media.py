"""Процессор для обработки медиа файлов (из main.py)."""

import os
import re
import shutil
import sys
from pathlib import Path
from typing import Match, Tuple
from urllib.parse import unquote, urlparse


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

    def process(
        self, content: str, input_path: Path, output_name: str | None = None
    ) -> Tuple[str, dict]:
        """
        Обработать медиа в Markdown.

        Returns:
            (обработанный_контент, media_map)
        """
        media_map = {}
        media_paths = self._extract_media_paths(content)

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

            decoded_path = unquote(media_path)

            # Пропускаем data URI (base64 встроенные изображения/шрифты)
            # Эти ресурсы уже встроены, искать файл не нужно
            if decoded_path.startswith("data:"):
                continue

            # Пропускаем уже обработанные пути (один файл упомянут несколько раз).
            # Без этого str.replace во второй итерации попадает в уже подставленный
            # абсолютный путь и задваивает его: C:/media/C:/media/hb_09.webp
            if media_path in media_map:
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
                        new_path = self._relative_output_path(
                            target_path, output_name
                        )
                        content = self._replace_media_path(
                            content, media_path, new_path
                        )
                        media_map[media_path] = new_path
                    else:
                        shutil.copy2(abs_path, target_path)
                        new_path = self._relative_output_path(
                            target_path, output_name
                        )
                        content = self._replace_media_path(
                            content, media_path, new_path
                        )
                        media_map[media_path] = new_path
                        print(f"  📎 {abs_path.name}", file=sys.stderr)
                        print(f"     ├─ источник: {abs_path}", file=sys.stderr)
                        print(f"     └─ скопирован → {new_path}", file=sys.stderr)
                else:
                    # EMBED режим - заменяем на file:// URI для Pandoc
                    # Абсолютный путь Windows (C:\...) Pandoc 3.x трактует как
                    # относительный и задваивает путь при --embed-resources
                    resolved = abs_path.resolve()
                    # Используем путь с прямыми слэшами — Pandoc понимает C:/...
                    # as_uri() URL-кодирует кириллицу → Pandoc не находит файл
                    normalized_path = str(resolved).replace("\\", "/")
                    content = self._replace_media_path(
                        content, media_path, normalized_path
                    )
                    media_map[media_path] = normalized_path
                    print(f"  📎 {abs_path.name}", file=sys.stderr)
                    print(f"     ├─ источник: {abs_path}", file=sys.stderr)
                    print(
                        f"     └─ будет встроен (EMBED: {normalized_path})",
                        file=sys.stderr,
                    )
            else:
                # Файл не найден - выводим все места поиска
                print(f"  ⚠️ НЕ НАЙДЕН: {decoded_path}", file=sys.stderr)
                print(f"     Искали в:", file=sys.stderr)
                for location in search_locations:
                    print(f"     - {location}", file=sys.stderr)

        return content, media_map

    @staticmethod
    def _is_local_media_path(path: str) -> bool:
        """True для локальных ресурсов, которые нужно копировать/встраивать."""
        if not path:
            return False
        decoded = unquote(path).strip()
        if decoded.startswith(("#", "data:")):
            return False
        parsed = urlparse(decoded)
        if parsed.scheme and parsed.scheme.lower() != "file":
            return False
        return True

    @classmethod
    def _extract_media_paths(cls, content: str) -> list[str]:
        """Найти Markdown media и raw HTML img/audio/video/source src."""
        media_paths: list[str] = []

        # Стандартный Markdown media: ![alt](path). Обычные ссылки не трогаем.
        for path in re.findall(r"!\[[^\]]*\]\((.*?)\)", content):
            if cls._is_local_media_path(path):
                media_paths.append(path)

        # Raw HTML media tags. Визуальные fixture часто вставляют audio/video
        # напрямую, поэтому их нужно валидировать и упаковывать как изображения.
        html_src_pattern = re.compile(
            r"<(?:img|audio|video|source)\b[^>]*\bsrc\s*=\s*(['\"])(.*?)\1",
            re.IGNORECASE | re.DOTALL,
        )
        for _quote, path in html_src_pattern.findall(content):
            if cls._is_local_media_path(path):
                media_paths.append(path)

        return media_paths

    def _relative_output_path(self, target_path: Path, output_name: str | None) -> str:
        """Путь к скопированному ресурсу относительно фактического HTML файла."""
        if output_name:
            html_parent = (self.output_dir / f"{output_name}.html").parent
        else:
            html_parent = self.output_dir
        rel_path = os.path.relpath(target_path, start=html_parent)
        return rel_path.replace(os.sep, "/")

    @staticmethod
    def _replace_media_path(content: str, old_path: str, new_path: str) -> str:
        """Заменить путь к медиа файлу в Markdown и HTML media src."""
        escaped = re.escape(old_path)
        # 1. Стандартный Markdown: ![alt](old_path) → ![alt](new_path)
        def replace_markdown_media(match: Match[str]) -> str:
            return match.group(1) + new_path + match.group(2)

        content = re.sub(
            r"(!\[.*?\]\()" + escaped + r"(\))",
            replace_markdown_media,
            content,
        )
        # 2. Raw HTML media src: <img/audio/video/source src="old_path">
        def replace_html_media(match: Match[str]) -> str:
            return match.group(1) + match.group(2) + new_path + match.group(2)

        content = re.sub(
            r"(<(?:img|audio|video|source)\b[^>]*\bsrc\s*=\s*)(['\"])"
            + escaped
            + r"\2",
            replace_html_media,
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        return content

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

"""Препроцессор для Obsidian-специфичного синтаксиса."""

import re
from pathlib import Path
from typing import Optional
from .base import Preprocessor


AUDIO_EXTENSIONS = {".mp3", ".m4a", ".ogg", ".opus", ".wav", ".flac", ".aac"}
VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".m4v", ".avi", ".mkv"}


class ObsidianPreprocessor(Preprocessor):
    """
    Обрабатывает Obsidian-специфичный синтаксис:
    - ![[image.png]] → ![](найденный_путь/image.png)
    - [[link]] → [link](link.md)

    Ищет изображения в папках:
    - текущая папка
    - attachments/
    - assets/
    - _attachments/
    - ../attachments/
    """

    def __init__(self, base_path: Optional[Path] = None):
        """Args: base_path - базовая папка для поиска файлов (папка MD файла)."""
        self.base_path = base_path or Path.cwd()

    def _find_attachment(self, filename: str) -> str:
        """Поиск файла в Obsidian attachment папках."""
        # Возможные папки для поиска (Obsidian стандарты)
        search_dirs = [
            self.base_path,
            self.base_path / "attachments",
            self.base_path / "_attachments",
            self.base_path / "assets",
            self.base_path.parent / "attachments",
            self.base_path.parent / "_attachments",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            # Прямой поиск
            candidate = search_dir / filename
            if candidate.exists():
                # ИСПРАВЛЕНИЕ БАГ #11: try/except для relative_to
                try:
                    return str(candidate.relative_to(self.base_path))
                except ValueError:
                    return str(candidate)  # Fallback на абсолютный путь

            # Рекурсивный поиск (если файл в подпапках)
            for file_path in search_dir.rglob(filename):
                if file_path.is_file():
                    try:
                        return str(file_path.relative_to(self.base_path))
                    except ValueError:
                        return str(file_path)

        # Не найден - возвращаем оригинальное имя
        return filename

    def _strip_frontmatter(self, content: str) -> str:
        """Удаление YAML frontmatter (--- ... ---) из начала документа."""
        # Frontmatter должен начинаться с самого начала файла
        frontmatter_pattern = re.compile(
            r"\A---\s*\n(.*?)\n---\s*\n",
            re.DOTALL,
        )
        return frontmatter_pattern.sub("", content)

    def _normalize_horizontal_rules(self, content: str) -> str:
        """Замена --- горизонтальных линий на *** для корректной обработки Pandoc.

        Pandoc может интерпретировать '---' как разделитель simple_table,
        особенно если после --- нет пустой строки. '***' однозначно
        является thematic break и не вызывает конфликтов.
        Вызывается ПОСЛЕ удаления frontmatter, так что оставшиеся --- это линии.
        """
        return re.sub(r"^---\s*$", "***", content, flags=re.MULTILINE)

    def _normalize_block_boundaries(self, content: str) -> str:
        """Добавить пустые строки вокруг блочных элементов Obsidian-заметки.

        В Obsidian часто пишут подряд embed/caption/heading или wikilink/---/текст.
        Pandoc без пустой строки может склеить следующий heading или thematic break
        с предыдущим абзацем, и в HTML появляются буквальные "##" или "***".
        """
        normalized: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            is_rule = stripped == "***"
            is_heading = bool(re.match(r"#{1,6}\s+", stripped))

            if (is_rule or is_heading) and normalized and normalized[-1].strip():
                normalized.append("")

            normalized.append(line)

            if is_rule:
                normalized.append("")

        return "\n".join(normalized) + ("\n" if content.endswith("\n") else "")

    @staticmethod
    def _media_embed_html(path: str, width: str | None = None) -> str | None:
        """HTML для Obsidian audio/video embeds; None для обычных изображений."""
        suffix = Path(path).suffix.lower()
        if suffix in AUDIO_EXTENSIONS:
            return f'<audio controls src="{path}"></audio>'
        if suffix in VIDEO_EXTENSIONS:
            width_attr = f' width="{width}"' if width and width.isdigit() else ""
            return f'<video controls src="{path}"{width_attr}></video>'
        return None

    def process(self, content: str) -> str:
        """Преобразование Obsidian синтаксиса."""

        # 0. Удаляем YAML frontmatter (метаданные Obsidian)
        content = self._strip_frontmatter(content)

        # 0.1 Нормализуем горизонтальные линии --- → ***
        content = self._normalize_horizontal_rules(content)

        # 0.2 Разделяем блочные элементы, которые Obsidian терпит,
        # но Pandoc может склеить с соседним абзацем.
        content = self._normalize_block_boundaries(content)

        # ![[file]] или ![[file|width]] → ![](найденный_путь) с опциональной шириной
        def replace_image(match):
            raw = match.group(1)
            # Разделяем имя файла и размер: ![[image.webp|500]]
            if "|" in raw:
                filename, size_str = raw.rsplit("|", 1)
                filename = filename.strip()
                size_str = size_str.strip()
                found_path = self._find_attachment(filename)
                media_html = self._media_embed_html(found_path, size_str)
                if media_html:
                    return media_html
                # Если size - число, трактуем как ширину
                if size_str.isdigit():
                    return f'<img src="{found_path}" width="{size_str}" />'
                # Иначе size_str это alt-текст (Obsidian поддерживает |alt)
                return f"![{size_str}]({found_path})"
            else:
                filename = raw.strip()
                found_path = self._find_attachment(filename)
                media_html = self._media_embed_html(found_path)
                if media_html:
                    return media_html
                return f"![]({found_path})"

        content = re.sub(r"!\[\[(.*?)\]\]", replace_image, content)

        # [[link]] → [link](link.md)
        def replace_link(match):
            full_text = match.group(1)
            if "|" in full_text:
                link, display = full_text.split("|", 1)
                target = link.strip()
                if not target.endswith(".md"):
                    target = f"{target}.md"
                return f"[{display.strip()}]({target})"
            else:
                target = full_text.strip()
                if not target.endswith(".md"):
                    target = f"{target}.md"
                return f"[{full_text}]({target})"

        content = re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)

        return content

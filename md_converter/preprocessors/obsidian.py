"""Препроцессор для Obsidian-специфичного синтаксиса."""

import re
from pathlib import Path
from .base import Preprocessor


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

    def __init__(self, base_path: Path = None):
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

    def process(self, content: str) -> str:
        """Преобразование Obsidian синтаксиса."""

        # ![[file]] → ![](найденный_путь)
        def replace_image(match):
            filename = match.group(1)
            found_path = self._find_attachment(filename)
            # Убираем alt текст, ставим пустой
            return f"![]({found_path})"

        content = re.sub(r"!\[\[(.*?)\]\]", replace_image, content)

        # ИСПРАВЛЕНИЕ БАГ #8: [[link]] → [link](#slug) вместо .md
        def replace_link(match):
            full_text = match.group(1)
            if "|" in full_text:
                link, display = full_text.split("|", 1)
                # Создаём slug для якоря (lowercase, пробелы → дефисы)
                slug = link.strip().lower().replace(" ", "-").replace("_", "-")
                return f"[{display.strip()}](#{slug})"
            else:
                slug = full_text.lower().replace(" ", "-").replace("_", "-")
                return f"[{full_text}](#{slug})"

        content = re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)

        return content

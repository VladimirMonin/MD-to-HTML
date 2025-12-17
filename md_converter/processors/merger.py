"""Процессор для склейки MD файлов из папки."""

import os
from pathlib import Path
from natsort import natsorted


class MergerProcessor:
    """Склеивает Markdown файлы из папки в один документ."""

    def merge(self, input_path: str | Path) -> str:
        """
        Читает и склеивает MD файлы.

        Args:
            input_path: Путь к файлу или папке

        Returns:
            Объединенный Markdown текст
        """
        input_path = Path(input_path)

        if input_path.is_file():
            # Один файл
            print(f"--- Обрабатываем файл: {input_path.name} ---")
            return input_path.read_text(encoding="utf-8")

        elif input_path.is_dir():
            # Папка с файлами
            md_files = [f for f in input_path.glob("*.md")]
            sorted_files = natsorted(md_files, key=lambda f: f.name)

            print(f"--- Сшиваем файлы ({len(sorted_files)} шт) ---")
            merged_content = []

            for file_path in sorted_files:
                print(f"  • {file_path.name}")
                content = file_path.read_text(encoding="utf-8")
                merged_content.append(content)

            return "\n\n".join(merged_content)

        else:
            raise ValueError(f"Путь не существует: {input_path}")

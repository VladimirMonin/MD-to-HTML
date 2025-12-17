"""Pandoc backend для конвертации (перенесено из build_book.py)."""

import os
import subprocess
from pathlib import Path
from ..config import ConverterConfig


class PandocBackend:
    """Backend для конвертации через Pandoc."""

    def __init__(self, config: ConverterConfig):
        """
        Args:
            config: Конфигурация конвертера
        """
        self.config = config

    def convert(
        self,
        content: str,
        output_name: str,
        format_type: str,
        header: str = "",
        media_map: dict = None,
    ) -> Path:
        """
        Конвертирует Markdown в HTML или EPUB через Pandoc.

        Args:
            content: Markdown текст
            output_name: Имя выходного файла (без расширения)
            format_type: "html" или "epub"
            header: HTML header для вставки
            media_map: Мапа медиа файлов (для режима copy)

        Returns:
            Путь к созданному файлу
        """
        # Создаем папку результата
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Сохраняем временный MD файл
        temp_md = output_dir / "_temp_merged.md"
        temp_md.write_text(content, encoding="utf-8")

        # Формируем команду Pandoc
        output_ext = "epub" if format_type == "epub" else "html"
        output_file = output_dir / f"{output_name}.{output_ext}"

        cmd = [
            "pandoc",
            str(temp_md),
            "-o",
            str(output_file),
            "--standalone",
        ]

        # TOC
        if self.config.features.toc:
            cmd.extend(["--toc", f"--toc-depth={self.config.features.toc_depth}"])

        # Метаданные
        if self.config.metadata.title:
            cmd.extend(["--metadata", f"title={self.config.metadata.title}"])
        else:
            cmd.extend(["--metadata", f"title={output_name}"])

        if self.config.metadata.author:
            cmd.extend(["--metadata", f"author={self.config.metadata.author}"])

        # CSS
        cmd.extend(["--css", "assets/css/book_style.css"])

        # Формат-специфичные настройки
        if format_type == "html":
            self._configure_html(cmd, header, output_dir)
        else:
            self._configure_epub(cmd)

        # Дополнительные аргументы
        cmd.extend(self.config.advanced.pandoc_extra_args)

        print(f"\n🚀 Запуск Pandoc для {format_type.upper()}...")
        print(f"Команда: {' '.join(cmd)}")

        # Окружение для mermaid-filter
        env = os.environ.copy()
        if format_type == "epub" and self.config.features.mermaid:
            env["MERMAID_FILTER_FORMAT"] = "svg"
            env["MERMAID_FILTER_THEME"] = self.config.styles.mermaid_theme
            env["MERMAID_FILTER_WIDTH"] = "1200"

        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, env=env
            )
            print(f"✅ Готово! Файл: {output_file}")
            return output_file

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка Pandoc:")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            raise

    def _configure_html(self, cmd: list, header: str, output_dir: Path):
        """Настройки для HTML."""
        # Отключаем встроенную подсветку (используем highlight.js)
        cmd.append("--no-highlight")

        # Встраиваем ресурсы
        if self.config.media_mode == "embed":
            cmd.append("--embed-resources")

        # Header с JS/CSS
        if header:
            header_file = output_dir / "_header.html"
            header_file.write_text(header, encoding="utf-8")
            cmd.extend(["--include-in-header", str(header_file)])

        cmd.append("--to=html5")

    def _configure_epub(self, cmd: list):
        """Настройки для EPUB."""
        # Тема подсветки
        theme_file = self.config.styles.highlight_theme
        if Path(theme_file).exists():
            cmd.extend(["--highlight-style", theme_file])
        else:
            cmd.extend(["--highlight-style", f"assets/{theme_file}.theme"])

        # Встраивание шрифтов
        if self.config.fonts.embed:
            fonts_dir = Path(self.config.fonts.dir)
            if fonts_dir.exists():
                print(f"📎 Вшиваем шрифты из {fonts_dir}...")
                for font_file in fonts_dir.glob("*.ttf"):
                    cmd.extend(["--epub-embed-font", str(font_file)])
                    print(f"  • {font_file.name}")

        # Mermaid filter
        if self.config.features.mermaid:
            # Windows использует .cmd wrapper
            mermaid_filter = (
                "mermaid-filter.cmd" if os.name == "nt" else "mermaid-filter"
            )
            cmd.extend(["-F", mermaid_filter])
            print("🎨 Mermaid: format=svg, theme=neutral")

        cmd.append("--to=epub3")

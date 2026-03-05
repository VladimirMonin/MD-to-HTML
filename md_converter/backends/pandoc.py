"""Pandoc backend для конвертации (перенесено из build_book.py)."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
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
        media_map: Optional[dict] = None,
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
            "--from",
            "markdown-yaml_metadata_block+fenced_divs",  # Добавляем fenced_divs для callouts
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

        if self.config.metadata.author:
            cmd.extend(["--metadata", f"author={self.config.metadata.author}"])

        # CSS - используем абсолютный путь от корня проекта
        # Предполагаем, что скрипт запущен из корня проекта
        css_path = Path("assets/css/book_style.css").resolve()
        if css_path.exists():
            cmd.extend(["--css", str(css_path)])
        else:
            print(f"⚠️ CSS файл не найден: {css_path}", file=sys.stderr)

        # Формат-специфичные настройки
        if format_type == "html":
            self._configure_html(cmd, header, output_dir)
        else:
            self._configure_epub(cmd)

        # Дополнительные аргументы
        cmd.extend(self.config.advanced.pandoc_extra_args)

        print(f"\n🚀 Запуск Pandoc для {format_type.upper()}...", file=sys.stderr)
        print(f"Команда: {' '.join(cmd)}", file=sys.stderr)

        # Окружение для mermaid-filter
        env = os.environ.copy()
        if format_type == "epub" and self.config.features.mermaid:
            env["MERMAID_FILTER_FORMAT"] = "svg"
            env["MERMAID_FILTER_THEME"] = self.config.styles.mermaid_theme
            env["MERMAID_FILTER_WIDTH"] = "1200"

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                env=env,
                timeout=300,  # 5 минут максимум для Pandoc
                stdin=subprocess.DEVNULL,  # Закрыть stdin чтобы не блокировать MCP stdio
            )
            print(f"✅ Готово! Файл: {output_file}", file=sys.stderr)
            return output_file

        except subprocess.TimeoutExpired:
            raise RuntimeError(
                f"Pandoc превысил таймаут (5 минут). Возможно документ слишком большой или есть проблемы с медиа файлами."
            )

        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка Pandoc:", file=sys.stderr)
            print(f"STDOUT: {e.stdout}", file=sys.stderr)
            print(f"STDERR: {e.stderr}", file=sys.stderr)
            # Формируем детальное сообщение об ошибке для GUI
            error_msg = f"Pandoc завершился с ошибкой (код {e.returncode})\n\n"
            if e.stderr:
                error_msg += f"STDERR:\n{e.stderr}\n\n"
            if e.stdout:
                error_msg += f"STDOUT:\n{e.stdout}\n\n"
            if not e.stderr and not e.stdout:
                error_msg += "Нет вывода от Pandoc. Возможные причины: кириллица в пути, недоступные ресурсы в --embed-resources, или повреждённый входной файл."
            raise RuntimeError(error_msg) from e

    def _configure_html(self, cmd: list, header: str, output_dir: Path):
        """Настройки для HTML."""
        # Отключаем встроенную подсветку (используем highlight.js)
        cmd.append("--syntax-highlighting=none")

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
                print(f"📎 Вшиваем шрифты из {fonts_dir}...", file=sys.stderr)
                for font_file in fonts_dir.glob("*.ttf"):
                    cmd.extend(["--epub-embed-font", str(font_file)])
                    print(f"  • {font_file.name}", file=sys.stderr)

        # Mermaid filter
        if self.config.features.mermaid:
            # Windows использует .cmd wrapper
            mermaid_filter = (
                "mermaid-filter.cmd" if os.name == "nt" else "mermaid-filter"
            )
            cmd.extend(["-F", mermaid_filter])
            print("🎨 Mermaid: format=svg, theme=neutral", file=sys.stderr)

        cmd.append("--to=epub3")

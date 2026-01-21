"""Препроцессор для Mermaid диаграмм - рендеринг через CLI в WebP."""

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from .base import Preprocessor


class MermaidPreprocessor(Preprocessor):
    """
    Препроцессор для конвертации Mermaid диаграмм в статические изображения.

    Вместо текстового рендеринга через JavaScript, диаграммы конвертируются
    в изображения WebP через Mermaid CLI (mmdc) с высоким разрешением.

    Процесс:
    1. Находит все блоки ```mermaid
    2. Для каждого блока запускает mmdc для рендера в WebP
    3. Заменяет блок на Markdown-ссылку на изображение
    4. MediaProcessor затем обработает эти изображения (embed/copy)
    """

    def __init__(self, config, format_type: str = "html"):
        """
        Args:
            config: Объект конфигурации с настройками Mermaid
            format_type: "html" или "epub"
        """
        self.format_type = format_type

        # Извлекаем настройки из конфига
        self.theme = config.styles.mermaid_theme
        self.scale = config.styles.mermaid_scale
        self.format = config.styles.mermaid_format
        self.quality = config.styles.mermaid_quality
        self.background = config.styles.mermaid_background

        # Режим медиа и output_dir
        self.media_mode = config.media_mode
        self.output_dir = Path(config.output_dir)

        # Находим mmdc исполняемый файл
        self.mmdc_path = self._find_mmdc()

    def _find_mmdc(self) -> str:
        """
        Найти исполняемый файл mmdc с учетом специфики разных платформ.

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

    def _render_diagram(self, diagram_code: str, diagram_index: int) -> bytes:
        """
        Рендерит Mermaid диаграмму в WebP формат В ПАМЯТИ.

        Args:
            diagram_code: Код диаграммы Mermaid
            diagram_index: Порядковый номер диаграммы в документе

        Returns:
            bytes: WebP данные

        Raises:
            subprocess.CalledProcessError: Если рендеринг завершился с ошибкой
        """
        from PIL import Image
        import io

        # Создаём временный файл для исходного кода
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".mmd", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(diagram_code)
            tmp_path = Path(tmp_file.name)

        # Временный PNG
        png_path = tmp_path.with_suffix(".png")

        try:
            # Формируем команду для mmdc
            cmd = [
                self.mmdc_path,
                "-i",
                str(tmp_path),
                "-o",
                str(png_path),
                "-t",
                self.theme,
                "-s",
                str(self.scale),
                "-b",
                self.background,
            ]

            # Запускаем рендеринг в PNG
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                check=True,
                stdin=subprocess.DEVNULL,  # Не блокировать MCP stdio
            )

            # Читаем PNG в память
            png_bytes = png_path.read_bytes()

            # Конвертируем PNG -> WebP в памяти
            with Image.open(io.BytesIO(png_bytes)) as png_image:
                webp_buffer = io.BytesIO()
                png_image.save(webp_buffer, "WEBP", quality=self.quality, method=6)

            return webp_buffer.getvalue()

        finally:
            # Удаляем временные файлы (с небольшой задержкой для Windows)
            import time

            time.sleep(0.05)  # 50ms для освобождения файлов

            for path in [tmp_path, png_path]:
                try:
                    if path.exists():
                        path.unlink()
                except PermissionError:
                    pass  # Игнорируем, система удалит позже

    def process(self, content: str) -> str:
        """
        Обрабатывает все Mermaid блоки в документе.

        Для EPUB: оставляет как есть (обработает mermaid-filter Pandoc)
        Для HTML: конвертирует в изображения WebP
        """
        if self.format_type != "html":
            # Для EPUB оставляем как есть
            return content

        # Считаем общее количество диаграмм для прогресса
        all_matches = list(re.finditer(r"```mermaid\s*\n(.*?)```", content, re.DOTALL))
        total_diagrams = len(all_matches)
        if total_diagrams > 0:
            print(f"  📊 Найдено {total_diagrams} Mermaid диаграмм", file=sys.stderr)

        # Счётчик диаграмм для уникальных имён файлов
        diagram_counter = [0]  # Используем список для замыкания

        def replace_mermaid(match):
            """Замена блока Mermaid на ссылку на изображение."""
            diagram_code = match.group(1).strip()
            diagram_counter[0] += 1
            current = diagram_counter[0]

            # Логируем прогресс
            print(
                f"  📊 Рендеринг диаграммы {current}/{total_diagrams}...",
                file=sys.stderr,
            )

            try:
                # Рендерим в память
                webp_bytes = self._render_diagram(diagram_code, current)

                if self.media_mode == "copy":
                    # COPY: сохраняем в output_dir/media/
                    media_dir = self.output_dir / "media"
                    media_dir.mkdir(parents=True, exist_ok=True)

                    filename = f"diagram_{current}.webp"
                    filepath = media_dir / filename
                    filepath.write_bytes(webp_bytes)

                    # Ссылка на файл
                    return f"\n![Mermaid Diagram {current}](media/{filename})\n"
                else:
                    # EMBED: base64 напрямую в Markdown
                    import base64

                    b64_data = base64.b64encode(webp_bytes).decode("ascii")
                    data_uri = f"data:image/webp;base64,{b64_data}"
                    return f"\n![Mermaid Diagram {current}]({data_uri})\n"

            except subprocess.CalledProcessError as e:
                # Если рендеринг не удался - оставляем исходный блок с предупреждением
                error_msg = e.stderr if e.stderr else "Unknown error"
                return (
                    f"\n> **⚠️ Ошибка рендеринга Mermaid диаграммы #{current}**\n"
                    f"> {error_msg[:200]}\n"
                    f"\n```mermaid\n{diagram_code}\n```\n"
                )
            except Exception as e:
                # Любые другие ошибки
                return (
                    f"\n> **⚠️ Неожиданная ошибка при обработке диаграммы #{current}**\n"
                    f"> {str(e)[:200]}\n"
                    f"\n```mermaid\n{diagram_code}\n```\n"
                )

        # Заменяем все блоки ```mermaid
        content = re.sub(
            r"```mermaid\s*\n(.*?)```", replace_mermaid, content, flags=re.DOTALL
        )

        return content

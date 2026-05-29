"""Препроцессор для Mermaid диаграмм - рендеринг через CLI в WebP."""

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from .base import Preprocessor
from .mermaid_autofix import MermaidAutoFixPreprocessor
from md_converter.config import ConverterConfig


class MermaidQuoteError(ValueError):
    """Ошибка обработки подписей узлов Mermaid."""

    def __init__(self, message: str, problematic_node: str, diagram_preview: str):
        self.problematic_node = problematic_node
        self.diagram_preview = diagram_preview
        super().__init__(
            f"{message}\nПроблемный узел: {problematic_node}\nДиаграмма:\n{diagram_preview}"
        )


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

    def __init__(self, config=None, format_type: str = "html"):
        """
        Args:
            config: Объект конфигурации с настройками Mermaid
            format_type: "html" или "epub"
        """
        self.format_type = format_type
        if config is None:
            config = ConverterConfig()

        # Извлекаем настройки из конфига
        self.theme = config.styles.mermaid_theme
        self.scale = config.styles.mermaid_scale
        self.format = config.styles.mermaid_format
        self.quality = config.styles.mermaid_quality
        self.background = config.styles.mermaid_background

        # Режим медиа и output_dir
        self.media_mode = config.media_mode
        self.output_dir = Path(config.output_dir)

        # mmdc ищем лениво, только когда действительно надо рендерить.
        self.mmdc_path: str | None = None
        self._autofix = MermaidAutoFixPreprocessor(format_type=format_type)

    def _quote_node_label(self, node: str, label: str, open_part: str, close_part: str) -> str:
        if label.startswith('"') and label.endswith('"'):
            return node

        if label.count('"') % 2:
            preview = getattr(self, "_current_diagram_preview", "")
            raise MermaidQuoteError(
                "Незакрытая кавычка в подписи узла Mermaid",
                node,
                preview,
            )

        needs_quotes = any(ord(ch) > 127 for ch in label) or "@" in label
        if not needs_quotes:
            return node

        escaped = label.replace('"', r'\"')
        return f'{open_part}"{escaped}"{close_part}'

    def _fix_node_quotes(self, code: str) -> str:
        """Добавить кавычки к сложным подписям узлов Mermaid."""
        self._current_diagram_preview = "\n".join(code.splitlines()[:4])
        shapes = [
            ("[[", "]]"),
            ("[(", ")]"),  # database/cylinder node
            ("((", "))"),
            ("[", "]"),
            ("{", "}"),
            ("(", ")"),
        ]

        result = []
        i = 0
        in_quote = False

        while i < len(code):
            ch = code[i]
            if ch == '"' and (i == 0 or code[i - 1] != "\\"):
                in_quote = not in_quote
                result.append(ch)
                i += 1
                continue

            if in_quote or not (ch.isalpha() or ch == "_"):
                result.append(ch)
                i += 1
                continue

            start = i
            j = i + 1
            while j < len(code) and (code[j].isalnum() or code[j] in "_-"):
                j += 1

            matched = None
            for opening, closing in shapes:
                if code.startswith(opening, j):
                    matched = (opening, closing)
                    break

            if not matched:
                result.append(code[start:j])
                i = j
                continue

            opening, closing = matched
            label_start = j + len(opening)
            label_end = code.find(closing, label_start)
            if label_end == -1:
                result.append(code[start:j])
                i = j
                continue

            label = code[label_start:label_end]
            node = code[start : label_end + len(closing)]
            open_part = code[start:label_start]
            close_part = closing
            result.append(self._quote_node_label(node, label, open_part, close_part))
            i = label_end + len(closing)

        return "".join(result)

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

        # Попытка 1: Через shutil.which (работает если mmdc в PATH).
        # На Windows npm обычно кладёт .cmd-wrapper, на Unix — исполняемый mmdc.
        command_names = ["mmdc.cmd", "mmdc"] if sys.platform == "win32" else ["mmdc"]
        for command_name in command_names:
            mmdc = shutil.which(command_name)
            if mmdc:
                return mmdc

        # Попытка 2: npm prefix. Это покрывает пользовательские Node-инсталляции
        # вроде ~/.hermes/node на Linux и AppData\Roaming\npm на Windows,
        # не хардкодя путь под одну машину.
        try:
            npm_prefix = subprocess.run(
                ["npm", "prefix", "-g"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
                stdin=subprocess.DEVNULL,
            ).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            npm_prefix = ""

        if npm_prefix:
            npm_bin_dirs = [Path(npm_prefix)] if sys.platform == "win32" else [Path(npm_prefix) / "bin"]
            for npm_bin_dir in npm_bin_dirs:
                for command_name in command_names:
                    candidate = npm_bin_dir / command_name
                    if candidate.exists():
                        return str(candidate)

        # Попытка 3: Windows - проверяем стандартное расположение npm глобальных пакетов
        if sys.platform == "win32":
            npm_global = os.path.expanduser(r"~\AppData\Roaming\npm")

            # Windows использует .cmd обертку для Node.js скриптов
            for variant in ["mmdc.cmd", "mmdc"]:
                mmdc_path = os.path.join(npm_global, variant)
                if os.path.exists(mmdc_path):
                    return mmdc_path

        # Попытка 4: Unix - проверяем стандартные npm пути
        else:
            for npm_prefix in [
                os.path.expanduser("~/.hermes/node/bin"),
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

    def _auto_fix_diagram(self, diagram_code: str) -> str:
        """Применить Mermaid auto-fix к одному блоку без повторного парсинга Markdown."""
        diagram_type = diagram_code.strip().split()[0] if diagram_code.strip() else ""
        if diagram_type == "sequenceDiagram":
            return self._autofix._fix_sequence_diagram(diagram_code)
        if diagram_type == "classDiagram":
            return self._autofix._fix_class_diagram(diagram_code)
        return diagram_code

    def _source_debug_block(self, original_code: str, rendered_code: str, diagram_index: int) -> str:
        """
        Сохраняет исходник Mermaid в невидимом HTML-блоке рядом с картинкой.

        Это не влияет на визуальный результат, но оставляет документ проверяемым:
        можно увидеть, из какого Mermaid-кода была получена статическая картинка.
        Используем <script type="text/plain">, а не HTML-комментарий, потому что
        Mermaid-стрелки содержат "-->", что ломает комментарии.
        """
        if original_code == rendered_code:
            source = rendered_code
        else:
            source = (
                "<!-- original Mermaid source before auto-fix -->\n"
                f"{original_code}\n"
                "<!-- Mermaid source used for rendering -->\n"
                f"{rendered_code}"
            )

        return (
            f'\n<script type="text/plain" class="mermaid-source" data-diagram="{diagram_index}">\n'
            '<div class="mermaid">\n'
            f'{source}\n'
            '</div>\n'
            '</script>\n'
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
            if not self.mmdc_path:
                self.mmdc_path = self._find_mmdc()

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
            original_diagram_code = match.group(1).strip()
            diagram_counter[0] += 1
            current = diagram_counter[0]

            # Логируем прогресс
            print(
                f"  📊 Рендеринг диаграммы {current}/{total_diagrams}...",
                file=sys.stderr,
            )

            try:
                diagram_code = self._auto_fix_diagram(original_diagram_code)
                diagram_code = self._fix_node_quotes(diagram_code)
                source_block = self._source_debug_block(
                    original_diagram_code, diagram_code, current
                )

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
                    return f"{source_block}\n![Mermaid Diagram {current}](media/{filename})\n"
                else:
                    # EMBED: base64 напрямую в Markdown
                    import base64

                    b64_data = base64.b64encode(webp_bytes).decode("ascii")
                    data_uri = f"data:image/webp;base64,{b64_data}"
                    return f"{source_block}\n![Mermaid Diagram {current}]({data_uri})\n"

            except subprocess.CalledProcessError as e:
                # Если рендеринг не удался - оставляем исходный блок с предупреждением
                error_msg = e.stderr if e.stderr else "Unknown error"
                return (
                    f"\n> **⚠️ Ошибка рендеринга Mermaid диаграммы #{current}**\n"
                    f"> {error_msg[:200]}\n"
                    f"\n```mermaid\n{original_diagram_code}\n```\n"
                )
            except Exception as e:
                # Любые другие ошибки
                return (
                    f"\n> **⚠️ Неожиданная ошибка при обработке диаграммы #{current}**\n"
                    f"> {str(e)[:200]}\n"
                    f"\n```mermaid\n{original_diagram_code}\n```\n"
                )

        # Заменяем все блоки ```mermaid
        content = re.sub(
            r"```mermaid\s*\n(.*?)```", replace_mermaid, content, flags=re.DOTALL
        )

        return content

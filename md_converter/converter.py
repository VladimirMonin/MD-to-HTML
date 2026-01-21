"""Главный класс конвертера - оркестратор pipeline."""

import sys
from pathlib import Path
from typing import Optional, Union
from .config import ConverterConfig
from .preprocessors import (
    ObsidianPreprocessor,
    CalloutsPreprocessor,
    MermaidPreprocessor,
    DiffPreprocessor,
)
from .processors import MediaProcessor, MergerProcessor, TemplateProcessor
from .backends import PandocBackend
from .postprocessors import PlyrWrapPostprocessor


class Converter:
    """Оркестратор конвертации Markdown → HTML/EPUB."""

    def __init__(self, config: ConverterConfig):
        """
        Args:
            config: Конфигурация конвертера
        """
        self.config = config
        self._setup_pipeline()

    def _setup_pipeline(self):
        """Настройка pipeline на основе конфига."""
        # Препроцессоры (порядок важен!)
        self.preprocessors = []

        # ВАЖНО: ObsidianPreprocessor получает base_path для поиска attachments
        # base_path будет установлен в convert() после получения input_path
        self.obsidian_preprocessor = None  # Создадим позже

        if self.config.features.callouts:
            self.preprocessors.append(CalloutsPreprocessor())

        # Mermaid и Diff добавятся для каждого формата отдельно

        # Процессоры
        self.media_processor = MediaProcessor(
            mode=self.config.media_mode,
            files_folder=self.config.input.files_folder,
            output_dir=self.config.output_dir,
        )
        self.merger = MergerProcessor()
        self.template_processor = TemplateProcessor(
            template=self.config.template,
            features=self.config.features,
            styles=self.config.styles,
            media_mode=self.config.media_mode,  # Передаём режим медиа
        )

        # Backend
        self.backend = PandocBackend(self.config)

        # Постпроцессоры
        self.postprocessors = []
        if self.config.features.plyr:
            self.postprocessors.append(PlyrWrapPostprocessor())

    def convert(
        self, input_path: Union[str, Path], output_name: Optional[str] = None
    ) -> list[Path]:
        """
        Главный метод конвертации.

        Args:
            input_path: Путь к MD файлу или папке
            output_name: Имя выходного файла (без расширения)

        Returns:
            Список путей к созданным файлам
        """
        input_path = Path(input_path)
        output_name = output_name or input_path.stem
        results = []

        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"📚 MD-to-HTML Converter v2.0", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)

        # ИСПРАВЛЕНИЕ БАГ #12: Правильный base_path (папка с MD файлом)
        # Для файла: его parent, для папки: сама папка
        base_path = input_path.parent if input_path.is_file() else input_path
        self.obsidian_preprocessor = ObsidianPreprocessor(base_path=base_path)

        # 1. Склейка файлов
        print("🔗 Этап 1: Склейка файлов...", file=sys.stderr)
        content = self.merger.merge(input_path)
        print(f"  ✓ Получено {len(content)} символов\n", file=sys.stderr)

        # 1.5. Obsidian препроцессинг (ПЕРЕД обработкой медиа)
        if self.config.input.source_type == "obsidian":
            print("🔄 Obsidian → Markdown...", file=sys.stderr)
            content = self.obsidian_preprocessor.process(content)
            print("  ✓ Синтаксис преобразован\n", file=sys.stderr)

        # 1.7. Mermaid препроцессинг (ДО MediaProcessor!)
        # Важно: сначала конвертируем диаграммы в картинки,
        # затем MediaProcessor обработает их как обычные изображения
        if self.config.features.mermaid:
            print("📊 Mermaid → WebP...", file=sys.stderr)
            mermaid_pp = MermaidPreprocessor(self.config, format_type="html")
            content = mermaid_pp.process(content)
            print("  ✓ Диаграммы конвертированы\n", file=sys.stderr)

        # 2. Обработка медиа
        print("📎 Этап 2: Обработка медиа...", file=sys.stderr)
        # Передаём реальный input_path, чтобы относительные пути к медиа разрешались корректно
        content, media_map = self.media_processor.process(content, input_path)
        print(f"  ✓ Обработано {len(media_map)} медиа файлов\n", file=sys.stderr)

        # 3. Конвертация для каждого формата
        for fmt in self.config.formats:
            print(f"{'=' * 60}", file=sys.stderr)
            print(f"📝 Формат: {fmt.upper()}", file=sys.stderr)
            print(f"{'=' * 60}\n", file=sys.stderr)

            # Препроцессинг с учетом формата
            print("⚙️ Этап 3: Препроцессинг Markdown...", file=sys.stderr)
            processed_content = content

            # Базовые препроцессоры
            for preprocessor in self.preprocessors:
                processed_content = preprocessor.process(processed_content)

            # Формат-специфичные препроцессоры
            if self.config.features.diff_blocks:
                diff_pp = DiffPreprocessor()
                processed_content = diff_pp.process(processed_content)

            print("  ✓ Препроцессинг завершен\n", file=sys.stderr)

            # Подготовка header
            print("🎨 Этап 4: Генерация шаблона...", file=sys.stderr)
            header = self.template_processor.build_header(fmt)
            print("  ✓ Шаблон готов\n", file=sys.stderr)

            # Конвертация через Pandoc
            print("🔄 Этап 5: Pandoc конвертация...", file=sys.stderr)
            output_path = self.backend.convert(
                content=processed_content,
                output_name=output_name,
                format_type=fmt,
                header=header,
                media_map=media_map,
            )
            print(file=sys.stderr)

            # Постобработка (только HTML)
            if fmt == "html" and self.postprocessors:
                print("🔧 Этап 6: Постобработка HTML...", file=sys.stderr)
                html = output_path.read_text(encoding="utf-8")
                for postprocessor in self.postprocessors:
                    html = postprocessor.process(html)
                output_path.write_text(html, encoding="utf-8")
                print("  ✓ Постобработка завершена\n", file=sys.stderr)

            results.append(output_path)

        return results

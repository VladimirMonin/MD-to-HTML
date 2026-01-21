"""
Прямой тест EMBED режима без MCP - для диагностики зависания.
"""

import tempfile
import time
from pathlib import Path
from md_converter import Converter, ConverterConfig
from md_converter.config import (
    InputConfig,
    MetadataConfig,
    StylesConfig,
    FontsConfig,
    FeaturesConfig,
    AdvancedConfig,
)


def test_embed_direct():
    """Тест EMBED конвертации напрямую (без MCP)."""

    print("\n" + "=" * 60)
    print("ПРЯМОЙ ТЕСТ EMBED РЕЖИМА")
    print("=" * 60)

    # Создаём тестовый MD
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("""# Test Document

```mermaid
flowchart TD
    A[Start] --> B[End]
```

This is a test with **bold** and *italic*.
""")
        test_md = Path(f.name)

    output_dir = Path(tempfile.mkdtemp())

    print(f"\n📝 Входной файл: {test_md}")
    print(f"📁 Выходная папка: {output_dir}")

    try:
        # Создаём конфигурацию
        config = ConverterConfig(
            output_dir=str(output_dir),
            template="web",
            media_mode="embed",  # EMBED режим!
            formats=["html"],
            input=InputConfig(
                path=str(test_md),
                source_type="standard",
                files_folder=str(test_md.parent),
            ),
            metadata=MetadataConfig(title="", author="", lang="ru", brand_image=""),
            styles=StylesConfig(highlight_theme="github-dark", mermaid_theme="forest"),
            fonts=FontsConfig(embed=True, dir="assets/fonts"),
            features=FeaturesConfig(
                toc=True,
                toc_depth=2,
                breadcrumbs=True,
                code_copy=True,
                fullscreen=True,
                diff_blocks=True,
                callouts=True,
                mermaid=True,
                plyr=True,
            ),
            advanced=AdvancedConfig(pandoc_extra_args=[], custom_css=[], custom_js=[]),
        )

        # Конвертация с замером времени
        print(f"\n⏱️  Начинаю конвертацию в EMBED режиме...")
        start_time = time.time()

        converter = Converter(config)
        result = converter.convert(test_md)

        elapsed = time.time() - start_time

        print(f"\n✅ УСПЕХ!")
        print(f"   Время выполнения: {elapsed:.2f} секунд")
        print(f"   Создано файлов: {len(result)}")

        for file_path in result:
            if file_path.exists():
                size_kb = file_path.stat().st_size / 1024
                print(f"   📄 {file_path.name} - {size_kb:.2f} KB")
            else:
                print(f"   ❌ {file_path.name} - НЕ СОЗДАН")

        # Проверка что HTML содержит base64 (признак EMBED)
        html_file = result[0]
        html_content = html_file.read_text(encoding="utf-8")

        has_base64_fonts = "data:font/" in html_content
        has_base64_images = "data:image/" in html_content

        print(f"\n🔍 Проверка встраивания:")
        print(f"   Шрифты в base64: {'✅' if has_base64_fonts else '❌'}")
        print(f"   Изображения в base64: {'✅' if has_base64_images else '❌'}")

        if elapsed > 120:
            print(f"\n⚠️  ВНИМАНИЕ: Конвертация заняла больше 2 минут!")
            print(f"   Это может указывать на проблемы с ресурсами.")
        elif elapsed > 60:
            print(f"\n⏰ Время в пределах нормы (30-60 секунд ожидаемо для EMBED)")
        else:
            print(f"\n⚡ Быстрая конвертация!")

        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Очистка
        test_md.unlink(missing_ok=True)


if __name__ == "__main__":
    success = test_embed_direct()
    exit(0 if success else 1)

# API Documentation

## Python API

### Базовое использование

```python
from md_converter import Converter, ConverterConfig

# Загрузка конфига из YAML
config = ConverterConfig.from_yaml("config.yaml")

# Создание конвертера
converter = Converter(config)

# Конвертация
results = converter.convert("input.md", "output_name")

# results - список Path объектов
for path in results:
    print(f"Создан: {path}")
```

### Создание конфига программно

```python
from md_converter import ConverterConfig

# Пустой конфиг (значения по умолчанию)
config = ConverterConfig()

# Настройка параметров
config.formats = ["html", "epub"]
config.media_mode = "copy"
config.output_dir = "./output"
config.metadata.title = "Мой документ"
config.metadata.author = "Автор"

# Функции
config.features.toc = True
config.features.breadcrumbs = False
```

### Переопределение настроек

```python
# Загрузка базового конфига
config = ConverterConfig.from_yaml("config.yaml")

# Переопределение отдельных параметров
config.formats = ["html"]
config.metadata.title = "Новый заголовок"
config.features.mermaid = False
```

## Классы

### ConverterConfig

Главная конфигурация конвертера.

**Атрибуты:**

- `output_dir: str` - папка для результатов
- `template: str` - шаблон (book/web)
- `media_mode: str` - режим медиа (embed/copy)
- `formats: list[str]` - список форматов
- `input: InputConfig` - входные данные
- `metadata: MetadataConfig` - метаданные
- `styles: StylesConfig` - стили
- `fonts: FontsConfig` - шрифты
- `features: FeaturesConfig` - функции
- `advanced: AdvancedConfig` - расширенные настройки

**Методы:**

#### `from_yaml(path: Path) -> ConverterConfig`

Загрузка конфига из YAML файла.

```python
config = ConverterConfig.from_yaml("config.yaml")
```

#### `merge_cli_args(args: dict) -> None`

Переопределение настроек из CLI аргументов.

```python
config.merge_cli_args({
    "format": "both",
    "media": "copy",
    "title": "Новый заголовок"
})
```

### Converter

Главный класс для конвертации.

**Методы:**

#### `__init__(config: ConverterConfig)`

Создание конвертера с конфигурацией.

```python
converter = Converter(config)
```

#### `convert(input_path: str, output_name: Optional[str] = None) -> list[Path]`

Конвертация MD файла/папки.

**Параметры:**

- `input_path` - путь к MD файлу или папке
- `output_name` - имя выходного файла (без расширения). Если None, используется имя входного файла

**Возвращает:**
Список путей к созданным файлам (HTML и/или EPUB).

```python
results = converter.convert("input.md", "output")
# ['build/output.html', 'build/output.epub']
```

## Модули

### Preprocessors

Препроцессоры для обработки Markdown до Pandoc.

#### `ObsidianPreprocessor`

Конвертация Obsidian синтаксиса:

- `![[image.png]]` → `![image.png](image.png)`
- `[[link]]` → `[link](link.md)`

```python
from md_converter.preprocessors import ObsidianPreprocessor

prep = ObsidianPreprocessor()
result = prep.process(markdown_text)
```

#### `CalloutsPreprocessor`

Конвертация callouts в Pandoc divs:

- `> [!NOTE]` → `::: NOTE`

```python
from md_converter.preprocessors import CalloutsPreprocessor

prep = CalloutsPreprocessor()
result = prep.process(markdown_text)
```

#### `MermaidPreprocessor`

Подготовка Mermaid диаграмм:

- HTML: ` ```mermaid` → `<pre class="mermaid">`
- EPUB: оставляет как есть (для mermaid-filter)

```python
from md_converter.preprocessors import MermaidPreprocessor

prep = MermaidPreprocessor(format_type="html")
result = prep.process(markdown_text)
```

#### `DiffPreprocessor`

Преобразование diff блоков в HTML:

- ` ```diff-python` → `<div class="diff-wrapper">...</div>`

```python
from md_converter.preprocessors import DiffPreprocessor

prep = DiffPreprocessor()
result = prep.process(markdown_text)
```

### Processors

#### `MergerProcessor`

Слияние нескольких MD файлов в один.

```python
from md_converter.processors import MergerProcessor

merger = MergerProcessor()
content = merger.process(input_path, files_folder)
```

#### `MediaProcessor`

Обработка медиа файлов (embed/copy).

```python
from md_converter.processors import MediaProcessor

media = MediaProcessor(media_mode="copy", output_dir="build")
media.process(markdown_content, source_dir)
```

#### `TemplateProcessor`

Генерация HTML headers с CSS/JS.

```python
from md_converter.processors import TemplateProcessor

template = TemplateProcessor(config)
header = template.generate_header()
```

### Backends

#### `PandocBackend`

Wrapper для Pandoc конвертации.

```python
from md_converter.backends import PandocBackend

pandoc = PandocBackend(config)
output_files = pandoc.convert(
    input_file="input.md",
    output_name="output",
    formats=["html", "epub"]
)
```

### Postprocessors

#### `MermaidFixPostprocessor`

Исправление HTML entity в Mermaid:

- `--&gt;` → `-->`

```python
from md_converter.postprocessors import MermaidFixPostprocessor

fixer = MermaidFixPostprocessor()
fixer.process(html_file_path)
```

## Примеры использования

### Простая конвертация

```python
from md_converter import Converter, ConverterConfig

config = ConverterConfig()
config.formats = ["html"]

converter = Converter(config)
results = converter.convert("input.md")
print(f"Создано: {results[0]}")
```

### Книга с метаданными

```python
from md_converter import Converter, ConverterConfig

config = ConverterConfig()
config.formats = ["html", "epub"]
config.media_mode = "embed"
config.metadata.title = "Моя книга"
config.metadata.author = "Автор"
config.metadata.brand_image = "cover.png"
config.fonts.embed = True

converter = Converter(config)
results = converter.convert("book.md", "my_book")
```

### Веб-документация

```python
from md_converter import Converter, ConverterConfig

config = ConverterConfig.from_yaml("config.yaml")
config.template = "web"
config.media_mode = "copy"
config.features.breadcrumbs = True

converter = Converter(config)
results = converter.convert("docs/", "documentation")
```

### Batch обработка

```python
from pathlib import Path
from md_converter import Converter, ConverterConfig

config = ConverterConfig()
config.formats = ["html"]

converter = Converter(config)

md_files = Path("docs").glob("*.md")
for md_file in md_files:
    output_name = md_file.stem
    results = converter.convert(str(md_file), output_name)
    print(f"✓ {md_file.name} → {results[0].name}")
```

### Кастомная обработка

```python
from md_converter import ConverterConfig
from md_converter.preprocessors import ObsidianPreprocessor, MermaidPreprocessor

# Только препроцессинг
config = ConverterConfig()
markdown = Path("input.md").read_text()

# Обработка Obsidian синтаксиса
obs = ObsidianPreprocessor()
markdown = obs.process(markdown)

# Обработка Mermaid
merm = MermaidPreprocessor(format_type="html")
markdown = merm.process(markdown)

# Сохранение
Path("output_processed.md").write_text(markdown)
```

## Error Handling

```python
from md_converter import Converter, ConverterConfig
from pathlib import Path

config = ConverterConfig()
converter = Converter(config)

try:
    results = converter.convert("input.md")
except FileNotFoundError as e:
    print(f"Файл не найден: {e}")
except subprocess.CalledProcessError as e:
    print(f"Ошибка Pandoc: {e}")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
```

## Type Hints

Все классы и функции имеют type hints:

```python
from pathlib import Path
from md_converter import Converter, ConverterConfig

def process_book(input_file: str, output_name: str) -> list[Path]:
    config = ConverterConfig()
    converter = Converter(config)
    return converter.convert(input_file, output_name)
```

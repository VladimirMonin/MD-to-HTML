# MD to HTML/EPUB Converter v2.0

Профессиональный конвертер Markdown → HTML/EPUB с модульной архитектурой.

## 🚀 Быстрый старт

### Установка зависимостей

```bash
poetry install
```

### Использование

**CLI:**

```bash
python cli.py <input> [options]

# Примеры:
python cli.py doc/README.md -f html
python cli.py "result/День №1" -f both --title "День 1"
python cli.py test.md -m copy --no-breadcrumbs
```

**Python API:**

```bash
python convert.py
```

## 📋 Структура проекта

```
MD_to_HTML/
├── cli.py                  # CLI точка входа (argparse)
├── convert.py              # Python точка входа (YAML)
├── config.yaml             # Конфигурация по умолчанию
├── pyproject.toml          # Poetry зависимости
│
├── md_converter/           # Основной пакет
│   ├── __init__.py
│   ├── config.py           # Dataclass конфигурация
│   ├── converter.py        # Оркестратор (6-stage pipeline)
│   │
│   ├── preprocessors/      # Препроцессоры Markdown
│   │   ├── base.py         # Абстрактный класс
│   │   ├── obsidian.py     # ![[]] → ![]()
│   │   ├── callouts.py     # [!NOTE] → ::: note
│   │   ├── mermaid.py      # ```mermaid → <pre>
│   │   └── diff.py         # ```diff-python → HTML
│   │
│   ├── processors/         # Процессоры
│   │   ├── merger.py       # Слияние MD файлов
│   │   ├── media.py        # Обработка медиа (embed/copy)
│   │   └── template.py     # Генерация HTML headers
│   │
│   ├── backends/           # Бэкенды конвертации
│   │   └── pandoc.py       # Pandoc wrapper (HTML/EPUB)
│   │
│   └── postprocessors/     # Постпроцессоры
│       ├── mermaid_fix.py  # Исправление символов
│       └── plyr_wrap.py    # Аудио/видео wrapper
│
├── assets/                 # Ресурсы
│   ├── css/
│   │   ├── main.css        # Главный CSS (импорты)
│   │   └── modules/        # CSS модули
│   │       ├── fonts.css
│   │       ├── base.css
│   │       ├── components.css
│   │       ├── breadcrumbs.css
│   │       └── ...
│   │
│   ├── js/
│   │   ├── main_modules.js # Главный JS (ES6)
│   │   └── modules/        # JS модули
│   │       ├── codeCopy.js
│   │       ├── fullscreen.js
│   │       ├── breadcrumbs.js
│   │       └── ...
│   │
│   ├── templates/          # HTML шаблоны
│   │   ├── book.html       # Книжный вид
│   │   └── web.html        # Веб вид (Bootstrap)
│   │
│   └── fonts/              # Встроенные шрифты
│
├── build/                  # Выходные файлы
├── backup/                 # Старый код
└── doc/                    # Документация
```

## ⚙️ Конфигурация

**Полная документация:** [doc/CONFIG.md](doc/CONFIG.md)

Главный файл: `config.yaml` в корне проекта.

Основные параметры:

- `formats` - html, epub или оба
- `media_mode` - embed (встроить) или copy (в папку media/)
- `template` - book (минималистичный) или web (Bootstrap)
- `features` - toc, breadcrumbs, mermaid, code_copy и др.

CLI аргументы переопределяют config.yaml.

## 🔧 CLI

**Полная документация:** [doc/CLI_GUIDE.md](doc/CLI_GUIDE.md)

```bash
python cli.py <input> [options]
```

Основные опции:

- `-f, --format` - html | epub | both
- `-m, --media` - embed | copy
- `-t, --template` - book | web
- `--title`, `--author`, `--brand` - метаданные
- `--no-toc`, `--no-breadcrumbs` - отключение функций

Примеры:

```bash
# Простая конвертация
python cli.py doc/README.md

# Книга с обложкой
python cli.py "День №1" -f both --title "День 1" --brand cover.png

# Веб-документация
python cli.py docs/ -t web -m copy
```

## 🏗️ Архитектура

### Pipeline (6 стадий)

```
1. Merger         → Слияние MD файлов (natsort)
2. MediaProcessor → Обработка медиа (embed/copy)
3. Preprocessors  → Obsidian → Callouts → Mermaid → Diff
4. Template       → Генерация HTML <head> с CSS/JS
5. PandocBackend  → Конвертация Pandoc (HTML/EPUB)
6. Postprocessors → MermaidFix, PlyrWrap (только HTML)
```

### Модули

**Preprocessors** — обрабатывают Markdown до Pandoc:

- `ObsidianPreprocessor`: `![[image]]` → `![](image)`
- `CalloutPreprocessor`: `[!NOTE]` → `::: note`
- `MermaidPreprocessor`: ` ```mermaid` → `<pre class="mermaid">`
- `DiffPreprocessor`: ` ```diff-python` → HTML структура "Было/Стало"

**Processors** — обработка файлов:

- `MergerProcessor`: Слияние нескольких MD в один
- `MediaProcessor`: Копирование/встраивание медиа
- `TemplateProcessor`: Генерация HTML headers

**Backends** — конвертация:

- `PandocBackend`: Wrapper для Pandoc с конфигами HTML/EPUB

**Postprocessors** — доработка HTML:

- `MermaidFixPostprocessor`: Исправление `--&gt;` → `-->`
- `PlyrWrapPostprocessor`: Обертка аудио/видео в Plyr (TODO)

## 📚 Python API

**Полная документация:** [doc/API.md](doc/API.md)

```python
from md_converter import Converter, ConverterConfig

# Загрузка конфига
config = ConverterConfig.from_yaml("config.yaml")

# Настройка
config.formats = ["html"]
config.metadata.title = "Мой документ"

# Конвертация
converter = Converter(config)
results = converter.convert("input.md", "output")

for path in results:
    print(f"Создан: {path}")
```

## 🎨 CSS Модули

CSS разбит на отдельные модули для удобства:

- `fonts.css` — @font-face определения
- `base.css` — body, заголовки, параграфы
- `components.css` — код, цитаты, таблицы
- `admonitions.css` — выноски [!NOTE]
- `toc.css` — оглавление
- `breadcrumbs.css` — хлебные крошки
- `interactive.css` — кнопки копирования, fullscreen
- `diff.css` — diff блоки
- `responsive.css` — @media queries

## 🔌 JS ES6 Модули

JavaScript разбит на ES6 модули:

- `codeCopy.js` — кнопки копирования кода
- `fullscreen.js` — fullscreen изображений/SVG
- `breadcrumbs.js` — динамические breadcrumbs
- `smoothScroll.js` — плавная прокрутка TOC
- `mermaid.js` — инициализация Mermaid

Главный файл `main_modules.js` импортирует все модули.

## 📦 Зависимости

- **Python**: 3.9+
- **Poetry**: Управление зависимостями
- **Pandoc**: 3.7+ (для конвертации)
- **natsort**: Естественная сортировка файлов
- **PyYAML**: Парсинг конфигов
- **mermaid-filter**: npm пакет (для EPUB SVG)

### Установка Pandoc

**Windows:**

```bash
winget install pandoc
```

**Linux:**

```bash
sudo apt install pandoc
```

**macOS:**

```bash
brew install pandoc
```

### Установка mermaid-filter

```bash
npm install -g mermaid-filter
```

## 🧪 Тестирование

```bash
python test_new.py
```

Тесты проверяют:

- Загрузку YAML конфига
- Работу всех препроцессоров
- Базовую конвертацию MD → HTML

## 🔄 Миграция со старой версии

Старые файлы перемещены в `backup/`:

- `backup/build_book.py` — старый Pandoc wrapper
- `backup/main.py` — Python-markdown конвертер
- `backup/main.html` — Bootstrap шаблон

Новая архитектура объединяет оба подхода с полной модульностью.

## 📖 Лицензия

MIT License — см. [LICENSE](LICENSE)

## 🤝 Вклад

1. Создайте ветку: `git checkout -b feature/new-feature`
2. Коммит: `git commit -m "Add new feature"`
3. Commit: `git push origin feature/new-feature`
4. Pull Request

## � Документация

- 🚀 **[Быстрый старт](doc/QUICKSTART.md)** - установка и первый запуск
- ⚙️ **[Конфигурация](doc/CONFIG.md)** - настройка config.yaml
- 🔧 **[CLI Guide](doc/CLI_GUIDE.md)** - примеры использования CLI
- 📖 **[API](doc/API.md)** - Python API документация
- 🎨 **[JS Enhancements](doc/JS_ENHANCEMENTS.md)** - интерактивные функции

## 📞 Поддержка

- **Issues**: [GitHub Issues](https://github.com/VladimirMonin/MD-to-HTML/issues)
- **Pull Requests**: welcome!

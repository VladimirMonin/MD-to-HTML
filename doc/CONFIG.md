# Конфигурация

## config.yaml

Главный файл конфигурации находится в корне проекта.

### Полная структура

```yaml
# Общие настройки
output_dir: "./build"          # Папка для результатов
template: "book"               # book | web
media_mode: "embed"            # embed | copy
formats: ["html"]              # html, epub или оба

# Входные данные
input:
  path: ""                     # Путь к MD файлу/папке (заполняется в CLI)
  files_folder: ""             # Альтернатива: папка с MD файлами

# Метаданные
metadata:
  title: "Документ"
  author: "Автор"
  brand_image: ""              # Путь к обложке (для EPUB)

# Стили
styles:
  highlight_theme: "github-dark"   # Тема подсветки кода
  custom_css: []                   # Дополнительные CSS файлы

# Шрифты
fonts:
  embed: true                  # Встроить шрифты в EPUB
  fonts_dir: "assets/fonts"    # Папка со шрифтами

# Функции
features:
  toc: true                    # Оглавление
  toc_depth: 2                 # Глубина оглавления (1-3)
  breadcrumbs: true            # Хлебные крошки (навигация)
  code_copy: true              # Кнопки копирования кода
  fullscreen: true             # Fullscreen для изображений/диаграмм
  diff_blocks: true            # Блоки diff (Было/Стало)
  callouts: true               # Поддержка [!NOTE]
  mermaid: true                # Mermaid диаграммы
  plyr: true                   # Plyr player для видео/аудио

# Расширенные настройки
advanced:
  pandoc_extra_args: []        # Дополнительные аргументы Pandoc
  custom_js: []                # Дополнительные JS файлы
```

## Настройка форматов

### Только HTML

```yaml
formats: ["html"]
```

### Только EPUB

```yaml
formats: ["epub"]
```

### Оба формата

```yaml
formats: ["html", "epub"]
```

## Режимы медиа

### EMBED (встроенные медиа)

```yaml
media_mode: "embed"
```

**Преимущества:**

- Один самодостаточный HTML файл
- Можно открывать без интернета
- Легко отправлять по почте

**Недостатки:**

- Большой размер файла
- Медленнее загружается

### COPY (копирование медиа)

```yaml
media_mode: "copy"
```

**Преимущества:**

- Маленький размер HTML
- Быстрее загружается
- Можно редактировать медиа отдельно

**Недостатки:**

- Нужна папка media/ рядом с HTML
- Сложнее пересылать

## Шаблоны

### BOOK (книжный вид)

```yaml
template: "book"
```

Минималистичный дизайн для чтения:

- Центрированный контент (800px)
- Serif шрифты (Merriweather)
- Оглавление в документе
- Breadcrumbs сверху

### WEB (веб вид)

```yaml
template: "web"
```

Для веб-публикации:

- Bootstrap 5 layout
- Sidebar с TOC
- Адаптивная верстка
- Sans-serif шрифты

## Функции

### Оглавление (TOC)

```yaml
features:
  toc: true
  toc_depth: 2
```

Генерирует оглавление из заголовков H1-H3.

### Breadcrumbs (навигация)

```yaml
features:
  breadcrumbs: true
```

Динамические "хлебные крошки" сверху страницы:

- Показывают текущий H2/H3
- Dropdown для перехода между разделами
- Sticky (прилипают к верху)

### Mermaid диаграммы

```yaml
features:
  mermaid: true
```

Поддержка ` ```mermaid` блоков:

- HTML: интерактивные SVG
- EPUB: статичные SVG (через mermaid-filter)

### Блоки Diff

```yaml
features:
  diff_blocks: true
```

Блоки ` ```diff-python` отображаются как "Было/Стало":

```diff-python
---OLD---
старый код
---NEW---
новый код
```

### Callouts (выноски)

```yaml
features:
  callouts: true
```

Поддержка Obsidian-стиля:

```markdown
> [!NOTE] Заголовок
> Текст выноски
```

Типы: NOTE, TIP, WARNING, DANGER

## Переопределение из CLI

CLI аргументы имеют приоритет над config.yaml:

```bash
python cli.py input.md \
  --format both \
  --media copy \
  --template web \
  --no-breadcrumbs
```

## Примеры конфигов

### Для книги (EPUB + HTML)

```yaml
formats: ["html", "epub"]
media_mode: "embed"
template: "book"
metadata:
  title: "Моя книга"
  author: "Автор"
  brand_image: "covers/cover.png"
fonts:
  embed: true
features:
  toc: true
  mermaid: true
```

### Для веб-документации

```yaml
formats: ["html"]
media_mode: "copy"
template: "web"
features:
  toc: true
  breadcrumbs: true
  code_copy: true
  callouts: true
```

### Минималистичный (быстрая конвертация)

```yaml
formats: ["html"]
media_mode: "embed"
template: "book"
features:
  toc: false
  breadcrumbs: false
  mermaid: false
```

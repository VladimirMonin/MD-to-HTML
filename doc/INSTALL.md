# 📦 Инструкция по установке MD-to-HTML конвертера

## Требования

- **Windows** (тестировалось на Windows 10/11)
- **Python 3.10+**
- **uv** для управления Python-окружением
- **Node.js 16+** (для mermaid-filter)
- **Pandoc 3.x**

---

## Шаг 1: Установка Pandoc

### Скачать и установить

1. Перейти на <https://pandoc.org/installing.html>
2. Скачать Windows installer (`.msi`)
3. Запустить установщик
4. Проверить установку:

```powershell
pandoc --version
# Должно вывести: pandoc 3.x.x
```

---

## Шаг 2: Установка Node.js

### Скачать и установить

1. Перейти на <https://nodejs.org/>
2. Скачать LTS версию для Windows
3. Запустить установщик
4. Проверить установку:

```powershell
node --version
# Должно вывести: v18.x.x или выше

npm --version
# Должно вывести: 9.x.x или выше
```

---

## Шаг 3: Установка mermaid-filter

Этот фильтр нужен для рендеринга Mermaid диаграмм в EPUB:

```powershell
npm install --global mermaid-filter
```

### Проверка установки

```powershell
# Проверяем что mermaid-filter.cmd доступен
Get-Command mermaid-filter.cmd -ErrorAction SilentlyContinue

# Должен вывести путь типа:
# C:\Users\<username>\AppData\Roaming\npm\mermaid-filter.cmd
```

**⚠️ Важно для Windows:**

- Используется `mermaid-filter.cmd` (не просто `mermaid-filter`)
- Путь автоматически добавляется в PATH при установке npm пакетов

---

## Шаг 4: Установка Python зависимостей

### Клонировать репозиторий

```powershell
git clone https://github.com/VladimirMonin/MD-to-HTML.git
cd MD-to-HTML
```

### Установить Python зависимости

```powershell
uv sync --frozen --all-groups
```

**Что установится:**

- `natsort` - для естественной сортировки файлов (Глава 1, Глава 2, Глава 10...)

---

## Шаг 5: Проверка всех зависимостей

Запустите тестовую сборку:

```powershell
uv run python test_build.py
```

**Что должно произойти:**

- ✅ Сборка HTML файла
- ✅ Сборка EPUB файла
- ✅ Вшивание шрифтов (CascadiaCode, FiraCode, JetBrainsMono, NotoEmoji)
- ✅ Рендеринг Mermaid диаграмм в SVG

**Результат:**

```
✅ Тест завершен успешно! Созданы файлы:
  - ./build/13_html_processors_architecture.html
  - ./build/13_html_processors_architecture.epub
```

---

## Структура проекта

```
MD-to-HTML/
├── build_book.py          # Основной скрипт сборки
├── test_build.py          # Тестовый скрипт
├── pyproject.toml         # Python зависимости и метаданные проекта
├── uv.lock                # Зафиксированные версии зависимостей uv
├── assets/
│   ├── css/
│   │   └── book_style.css # Стили для HTML/EPUB
│   ├── fonts/             # Шрифты для EPUB
│   │   ├── CascadiaCode-Regular.ttf
│   │   ├── FiraCode-Regular.ttf
│   │   ├── JetBrainsMono-Regular.ttf
│   │   └── NotoEmoji.ttf
│   ├── js/
│   │   └── pandoc_enhancements.js # JS для HTML
│   └── github-dark.theme  # Кастомная тема подсветки
├── build/                 # Результаты сборки
└── doc/                   # Документация
```

---

## Использование

### Интерактивный режим

```powershell
uv run python build_book.py
```

**Вам предложат:**

1. Ввести путь к `.md` файлу или папке с файлами
2. Ввести имя выходного файла (без расширения)
3. Выбрать формат:
   - `1` - HTML
   - `2` - EPUB
   - `3` - HTML + EPUB

### Программный вызов

```python
from build_book import build_book

# HTML
build_book("path/to/markdown.md", "output_name", "html")

# EPUB
build_book("path/to/markdown.md", "output_name", "epub")
```

---

## Что установлено и для чего

### 1. **Pandoc** (обязательно)

- **Что:** Конвертер документов (Markdown → HTML/EPUB/PDF)
- **Зачем:** Основной движок конвертации
- **Команда проверки:** `pandoc --version`

### 2. **Node.js + npm** (обязательно)

- **Что:** JavaScript runtime и пакетный менеджер
- **Зачем:** Для установки mermaid-filter
- **Команда проверки:** `node --version`, `npm --version`

### 3. **mermaid-filter** (обязательно для EPUB с диаграммами)

- **Что:** Pandoc filter для рендеринга Mermaid
- **Зачем:** Преобразует Mermaid код в SVG/PNG для EPUB
- **Команда проверки:** `Get-Command mermaid-filter.cmd`

### 4. **Python + uv** (обязательно)

- **Что:** Python окружение и менеджер зависимостей
- **Зачем:** Запуск build_book.py
- **Команда проверки:** `python --version`, `uv --version`

### 5. **natsort** (Python пакет)

- **Что:** Библиотека для естественной сортировки
- **Зачем:** Правильная сортировка "Глава 1", "Глава 2", "Глава 10"
- **Устанавливается через:** `uv sync --frozen --all-groups`

---

## JS зависимости (только для HTML)

### Встроенные (CDN, автоматически)

#### 1. **Highlight.js** (подсветка синтаксиса)

```html
<!-- Автоматически вшивается в HTML -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
```

**Зачем:** Красивая подсветка кода (лучше чем Pandoc Skylighting)

#### 2. **Mermaid** (диаграммы)

```html
<!-- Автоматически вшивается в HTML -->
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
</script>
```

**Зачем:** Рендеринг Mermaid диаграмм в браузере

#### 3. **pandoc_enhancements.js** (кастомный)

```javascript
// Вшивается напрямую в HTML через --include-in-header
// Функции:
- Кнопки копирования кода
- Fullscreen для изображений и SVG
- Smooth scroll для TOC
```

**Зачем:** Интерактивные возможности HTML версии

---

## Особенности сборки

### HTML

- ✅ Highlight.js (github-dark тема)
- ✅ Mermaid (neutral тема, SVG)
- ✅ JavaScript enhancements (copy, fullscreen)
- ✅ CSS стили (градиентный TOC, тёмные блоки кода)
- ✅ Один файл с --embed-resources

### EPUB

- ✅ Pandoc Skylighting (кастомная github-dark тема)
- ✅ Mermaid через mermaid-filter (SVG в EPUB)
- ✅ Вшитые шрифты (JetBrains Mono, NotoEmoji)
- ✅ CSS стили (адаптированные для e-reader)
- ❌ JavaScript (не работает в EPUB readers)

---

## Возможные проблемы

### ❌ "mermaid-filter.cmd not found"

**Решение:**

```powershell
npm install --global mermaid-filter
# Перезапустить PowerShell
```

### ❌ "pandoc: command not found"

**Решение:** Переустановить Pandoc, проверить PATH

### ❌ Emoji не отображаются на PocketBook

**Причина:** Цветные emoji не поддерживаются
**Решение:** Используем монохромный NotoEmoji.ttf (уже в проекте)

### ❌ Диаграммы в EPUB показываются как код

**Причина:** mermaid-filter не установлен или не работает
**Проверка:** `Get-Command mermaid-filter.cmd`

### ❌ Шрифты не отображаются в EPUB

**Причина:** Читалка не поддерживает embedded fonts
**Решение:** Включить "Publisher Fonts" в настройках читалки

---

## Обновление зависимостей

### Обновить Pandoc

Скачать новую версию с <https://pandoc.org/>

### Обновить mermaid-filter

```powershell
npm update --global mermaid-filter
```

### Обновить Python зависимости

```powershell
uv lock --upgrade
```

---

## Дополнительная настройка

### Изменить тему подсветки кода (HTML)

В [build_book.py](build_book.py):

```python
HLJS_THEME = "github-dark"  # Измените на: dracula, monokai, atom-one-dark и т.д.
```

### Изменить тему Mermaid

В [build_book.py](build_book.py):

```python
MERMAID_THEME = "neutral"  # Измените на: default, dark, forest
```

### Изменить шрифты

Положите свои `.ttf` файлы в `assets/fonts/` - они автоматически вшиваются в EPUB

---

## Контакты и поддержка

- **Репозиторий:** <https://github.com/VladimirMonin/MD-to-HTML>
- **Issues:** <https://github.com/VladimirMonin/MD-to-HTML/issues>
- **Документация:** [doc/](doc/)

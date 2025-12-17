# CLI Guide

## Основы

```bash
python cli.py <input> [options]
```

## Позиционные аргументы

### `<input>` (обязательный)

Путь к MD файлу или папке с MD файлами.

```bash
# Один файл
python cli.py doc/README.md

# Папка с файлами
python cli.py "result/День №1"

# Относительный путь
python cli.py ./docs/guide.md
```

## Опции

### `-o, --output` - Имя выходного файла

```bash
python cli.py input.md -o my_output
# Результат: build/my_output.html
```

Без `-o` используется имя исходного файла.

### `-f, --format` - Формат вывода

```bash
# Только HTML (по умолчанию)
python cli.py input.md -f html

# Только EPUB
python cli.py input.md -f epub

# Оба формата
python cli.py input.md -f both
```

### `-m, --media` - Режим медиа

```bash
# EMBED - встроить медиа (по умолчанию)
python cli.py input.md -m embed

# COPY - скопировать в media/
python cli.py input.md -m copy
```

### `-t, --template` - Шаблон

```bash
# BOOK - книжный вид (по умолчанию)
python cli.py input.md -t book

# WEB - веб вид (Bootstrap)
python cli.py input.md -t web
```

### `-c, --config` - Путь к конфигу

```bash
python cli.py input.md -c custom_config.yaml
```

По умолчанию: `config.yaml`

## Метаданные

### `--title` - Заголовок документа

```bash
python cli.py input.md --title "Мой документ"
```

### `--author` - Автор

```bash
python cli.py input.md --author "Иван Иванов"
```

### `--brand` - Обложка (для EPUB)

```bash
python cli.py input.md --brand covers/cover.png
```

## Функции (отключение)

### `--no-toc` - Без оглавления

```bash
python cli.py input.md --no-toc
```

### `--no-breadcrumbs` - Без навигации

```bash
python cli.py input.md --no-breadcrumbs
```

### `--no-mermaid` - Без Mermaid

```bash
python cli.py input.md --no-mermaid
```

## Тема подсветки

### `--theme` - Тема кода

```bash
python cli.py input.md --theme zenburn
```

По умолчанию: `github-dark`

Доступные темы: см. [Highlight.js themes](https://highlightjs.org/examples)

## Примеры

### Простая конвертация

```bash
python cli.py doc/README.md
```

### Книга с обложкой

```bash
python cli.py "result/День №1" \
  -f both \
  --title "День 1 - Python основы" \
  --author "Vladimir Monin" \
  --brand covers/day1.png
```

### Веб-документация

```bash
python cli.py docs/ \
  -t web \
  -m copy \
  --title "API Documentation"
```

### Минимальный HTML

```bash
python cli.py input.md \
  -f html \
  --no-toc \
  --no-breadcrumbs \
  --no-mermaid
```

### Кастомный конфиг

```bash
python cli.py input.md \
  -c configs/production.yaml \
  -o production_build
```

### EPUB для e-reader

```bash
python cli.py book.md \
  -f epub \
  --title "Моя книга" \
  --author "Автор" \
  --brand cover.png
```

## Комбинирование опций

```bash
python cli.py "result/День №10" \
  --format both \
  --media copy \
  --template web \
  --title "День 10 - Декораторы" \
  --author "Vladimir" \
  --no-breadcrumbs \
  --theme monokai
```

## Troubleshooting

### "Путь не найден"

Используйте кавычки для путей с пробелами:

```bash
python cli.py "C:\Path with spaces\file.md"
```

### "Pandoc не найден"

Установите Pandoc:

```bash
winget install pandoc
```

### "Ошибка mermaid-filter"

Для EPUB с Mermaid установите:

```bash
npm install -g mermaid-filter
```

### "Неверный формат конфига"

Проверьте синтаксис YAML в config.yaml:

```bash
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

## Tips & Tricks

### Алиасы (Linux/Mac)

Добавьте в `~/.bashrc` или `~/.zshrc`:

```bash
alias mdconv="python ~/MD-to-HTML/cli.py"
```

Использование:

```bash
mdconv input.md -f both
```

### PowerShell функция (Windows)

Добавьте в профиль (`$PROFILE`):

```powershell
function mdconv {
    python C:\PY\MD_to_HTML\cli.py $args
}
```

### Batch обработка

```bash
for file in docs/*.md; do
    python cli.py "$file" -f html -o "output/$(basename "$file" .md)"
done
```

### Интеграция с VS Code

Создайте Task (`.vscode/tasks.json`):

```json
{
  "label": "Convert to HTML",
  "type": "shell",
  "command": "python",
  "args": ["cli.py", "${file}", "-f", "html"],
  "group": "build"
}
```

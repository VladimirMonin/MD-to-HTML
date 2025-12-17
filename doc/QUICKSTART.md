# Быстрый старт

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/VladimirMonin/MD-to-HTML.git
cd MD-to-HTML
```

### 2. Установка Python зависимостей

**Требования:**

- Python 3.9+
- Poetry (менеджер зависимостей)

```bash
# Установка Poetry (если еще не установлен)
curl -sSL https://install.python-poetry.org | python3 -

# Установка зависимостей проекта
poetry install
```

### 3. Установка Pandoc

**Windows:**

```bash
winget install pandoc
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install pandoc
```

**macOS:**

```bash
brew install pandoc
```

**Проверка установки:**

```bash
pandoc --version
# Должно показать версию 3.7+
```

### 4. Установка JS зависимостей (опционально)

Для EPUB с Mermaid диаграммами нужен `mermaid-filter`:

**Установка Node.js** (если еще нет):

- **Windows**: скачать с [nodejs.org](https://nodejs.org/)
- **Linux**: `sudo apt install nodejs npm`
- **macOS**: `brew install node`

**Установка mermaid-filter:**

```bash
npm install -g mermaid-filter
```

**Проверка:**

```bash
mermaid-filter --version
```

## Первый запуск

### CLI (быстрый способ)

```bash
poetry run python cli.py doc/README.md
```

Результат: `build/README.html`

### Интерактивное меню (пошаговый способ)

```bash
poetry run python convert.py
```

Программа задаст вопросы:

1. Путь к файлу/папке
2. Формат (HTML/EPUB/оба)
3. Режим медиа (embed/copy)
4. Шаблон (book/web)
5. Метаданные (заголовок, автор)
6. Дополнительные функции

## Что дальше?

- [Работа с конфигурацией](CONFIG.md)
- [Примеры использования CLI](CLI_GUIDE.md)
- [API документация](API.md)

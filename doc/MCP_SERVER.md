# MCP Server для MD-to-HTML конвертера

## Описание

MCP (Model Context Protocol) сервер для MD-to-HTML конвертера предоставляет высокоуровневый API для конвертации Markdown файлов в HTML через стандартный протокол MCP.

Сервер работает по протоколу `stdio` и может быть интегрирован с любыми MCP-совместимыми клиентами, включая:

- VS Code Copilot
- Claude Desktop
- Другие AI ассистенты с поддержкой MCP

## Возможности

Единый инструмент `convert_markdown_to_html` обеспечивает:

- ✅ **Полную валидацию**: проверка входного файла, папки медиа, выходного пути
- ✅ **Проверку медиа файлов**: автоматическая проверка наличия всех изображений/аудио/видео
- ✅ **Детальные ошибки**: специфические исключения с подробной информацией
- ✅ **Гибкие настройки**: TOC, хлебные крошки, шаблоны, режимы медиа
- ✅ **Поддержку всех фич**: Mermaid, callouts, diff блоки, Plyr и др.

## Установка

### 1. Установка зависимостей через uv

Рекомендуется использовать `uv` для быстрой установки:

```bash
cd C:\PY\MD_to_HTML
uv pip install -e .
```

Или через обычный pip:

```bash
cd C:\PY\MD_to_HTML
pip install -e .
```

Это установит пакет `mcp` (Model Context Protocol Python SDK) вместе с другими зависимостями.

### 2. Проверка установки

```bash
python mcp_server.py
```

Сервер должен запуститься и ожидать входящих MCP запросов через stdio.

## Конфигурация для VS Code

Добавьте следующую конфигурацию в ваш файл MCP настроек VS Code:

**Windows**: `%APPDATA%\Code\User\mcp.json`
**macOS/Linux**: `~/.config/Code/User/mcp.json`

```json
{
  "servers": {
    "md-to-html": {
      "type": "stdio",
      "command": "C:\\PY\\MD_to_HTML\\.venv\\Scripts\\python.exe",
      "args": ["C:\\PY\\MD_to_HTML\\mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1"
      },
      "autoApprove": [
        "convert_markdown_to_html"
      ],
      "disabled": false,
      "timeout": 1800
    }
  }
}
```

**Важно**: Замените пути на актуальные для вашей системы!

### Настройка путей

- **Windows с venv**:

  ```json
  "command": "C:\\PY\\MD_to_HTML\\.venv\\Scripts\\python.exe",
  "args": ["C:\\PY\\MD_to_HTML\\mcp_server.py"]
  ```

- **Windows без venv** (системный Python):

  ```json
  "command": "python",
  "args": ["C:\\PY\\MD_to_HTML\\mcp_server.py"]
  ```

- **Linux/macOS с venv**:

  ```json
  "command": "/home/user/projects/MD_to_HTML/.venv/bin/python",
  "args": ["/home/user/projects/MD_to_HTML/mcp_server.py"]
  ```

## Использование

После настройки MCP сервер автоматически становится доступен в GitHub Copilot в VS Code.

### Пример запроса к AI ассистенту

```
Конвертируй Markdown файл C:/docs/lesson.md в HTML. 
Медиа файлы находятся в C:/docs/media. 
Результат сохрани в C:/docs/output.
```

Или более детальный запрос:

```
Используй MCP сервер md-to-html для конвертации:
- Входной файл: C:/docs/tutorial.md
- Папка медиа: C:/docs/images
- Выходная директория: C:/docs/html
- Включи TOC с глубиной 3
- Используй шаблон web
- Режим медиа: embed
```

## API инструмента

### convert_markdown_to_html

Единственный инструмент сервера с полным набором параметров.

#### Обязательные параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `input_file` | str | Абсолютный путь к .md файлу |
| `media_folder` | str | Абсолютный путь к папке с медиа |
| `output_path` | str | Абсолютный путь к выходной директории |

#### Опциональные параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `enable_toc` | bool | True | Генерация оглавления |
| `toc_depth` | int | 2 | Глубина оглавления (1-6) |
| `enable_breadcrumbs` | bool | True | Хлебные крошки |
| `output_format` | str | "html" | Формат: "html" или "epub" |
| `template` | str | "web" | Шаблон: "web" или "book" |
| `media_mode` | str | "embed" | Режим: "embed" или "copy" |
| `validate_media` | bool | True | Проверять медиа перед конвертацией |

#### Возвращаемое значение

**Успех**:

```json
{
  "status": "success",
  "output_files": [
    "C:/docs/output/lesson.html"
  ],
  "stats": {
    "input_file": "C:/docs/lesson.md",
    "file_size": 12345,
    "media_files_found": 5,
    "media_files_missing": 0,
    "output_format": "html"
  },
  "message": "Конвертация успешно завершена"
}
```

**Ошибка**:

```json
{
  "status": "error",
  "error_type": "MediaFilesNotFoundError",
  "message": "Следующие медиа файлы не найдены (3): image1.png, video.mp4, audio.wav",
  "details": {
    "missing_files": [
      "image1.png",
      "video.mp4",
      "audio.wav"
    ],
    "total_missing": 3,
    "media_folder": "C:/docs/media"
  }
}
```

## Типы ошибок

Сервер возвращает специфические типы ошибок для детальной диагностики:

### 1. InputFileNotFoundError

Входной Markdown файл не найден или имеет неверное расширение.

```json
{
  "status": "error",
  "error_type": "InputFileNotFoundError",
  "message": "Входной файл не найден: C:/docs/missing.md",
  "details": {
    "input_file": "C:/docs/missing.md",
    "exists": false
  }
}
```

### 2. MediaFolderNotFoundError

Папка с медиа файлами не существует.

```json
{
  "status": "error",
  "error_type": "MediaFolderNotFoundError",
  "message": "Папка медиа не найдена: C:/docs/media",
  "details": {
    "media_folder": "C:/docs/media",
    "exists": false
  }
}
```

### 3. OutputPathNotFoundError

Невозможно создать выходную директорию.

```json
{
  "status": "error",
  "error_type": "OutputPathNotFoundError",
  "message": "Не удалось создать выходную директорию C:/invalid/path",
  "details": {
    "output_path": "C:/invalid/path",
    "exists": false
  }
}
```

### 4. MediaFilesNotFoundError

Некоторые медиа файлы, упомянутые в документе, отсутствуют.

```json
{
  "status": "error",
  "error_type": "MediaFilesNotFoundError",
  "message": "Следующие медиа файлы не найдены (2): diagram.png, screenshot.jpg",
  "details": {
    "missing_files": ["diagram.png", "screenshot.jpg"],
    "total_missing": 2,
    "media_folder": "C:/docs/media"
  }
}
```

## Примеры использования

### Базовая конвертация

```python
# Через MCP клиент
result = await mcp_client.call_tool(
    "convert_markdown_to_html",
    {
        "input_file": "C:/docs/lesson.md",
        "media_folder": "C:/docs/media",
        "output_path": "C:/docs/output"
    }
)
```

### С кастомными настройками

```python
result = await mcp_client.call_tool(
    "convert_markdown_to_html",
    {
        "input_file": "C:/docs/tutorial.md",
        "media_folder": "C:/docs/images",
        "output_path": "C:/docs/html",
        "enable_toc": True,
        "toc_depth": 3,
        "enable_breadcrumbs": True,
        "template": "web",
        "media_mode": "copy"
    }
)
```

### Без проверки медиа (быстрая конвертация)

```python
result = await mcp_client.call_tool(
    "convert_markdown_to_html",
    {
        "input_file": "C:/docs/draft.md",
        "media_folder": "C:/docs/media",
        "output_path": "C:/docs/output",
        "validate_media": False
    }
)
```

## Отладка

### Тестирование сервера

Запустите сервер вручную для проверки:

```bash
cd C:\PY\MD_to_HTML
python mcp_server.py
```

Сервер должен запуститься и ожидать JSON-RPC сообщений через stdin.

### Логирование

Для включения детального логирования добавьте переменную окружения:

```json
"env": {
  "PYTHONIOENCODING": "utf-8",
  "PYTHONUTF8": "1",
  "MCP_DEBUG": "1"
}
```

### Типичные проблемы

1. **Сервер не запускается**
   - Проверьте путь к Python интерпретатору
   - Убедитесь, что установлен пакет `mcp`
   - Проверьте права доступа к файлам

2. **Ошибка импорта модулей**
   - Убедитесь, что вы находитесь в правильной директории
   - Проверьте наличие `md_converter` пакета
   - Попробуйте `pip install -e .`

3. **Timeout ошибки**
   - Увеличьте значение `timeout` в конфигурации (особенно для больших файлов)
   - По умолчанию рекомендуется 600 секунд (10 минут)

## Интеграция с другими MCP клиентами

### Claude Desktop

Добавьте в `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "md-to-html": {
      "command": "python",
      "args": ["C:\\PY\\MD_to_HTML\\mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Программная интеграция

```python
import asyncio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

async def convert_with_mcp():
    async with stdio_client(
        StdioServerParameters(
            command="python",
            args=["C:\\PY\\MD_to_HTML\\mcp_server.py"]
        )
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            result = await session.call_tool(
                "convert_markdown_to_html",
                {
                    "input_file": "C:/docs/lesson.md",
                    "media_folder": "C:/docs/media",
                    "output_path": "C:/docs/output"
                }
            )
            
            print(result)

asyncio.run(convert_with_mcp())
```

## Дополнительная информация

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/fastmcp.md)

## Лицензия

MIT License - см. LICENSE файл в корне проекта.

# Быстрый старт MCP Server для MD-to-HTML

## За 3 шага

### 1. Установка

```bash
cd C:\PY\MD_to_HTML
uv pip install -e .
```

### 2. Добавление в VS Code

Откройте файл конфигурации MCP:

- Windows: `%APPDATA%\Code\User\mcp.json`
- macOS/Linux: `~/.config/Code/User/mcp.json`

Добавьте (измените пути под вашу систему):

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

### 3. Использование

Перезапустите VS Code и обратитесь к Copilot:

```
Конвертируй файл C:/docs/lesson.md в HTML.
Медиа в C:/docs/media, результат в C:/docs/output.
```

## Полная документация

См. [MCP_SERVER.md](MCP_SERVER.md) для детальной информации о:

- API инструмента
- Параметрах конфигурации
- Обработке ошибок
- Примерах использования
- Отладке

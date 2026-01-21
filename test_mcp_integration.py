"""
Интеграционный тест MCP сервера.
Эмулирует реальную работу через Model Context Protocol.
"""

import json
import subprocess
import sys
import tempfile
import threading
from pathlib import Path


def read_with_timeout(stream, timeout=60):
    """Читает из потока с таймаутом. Возвращает строку или None при таймауте."""
    result = [None]

    def reader():
        try:
            result[0] = stream.readline()
        except:
            pass

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout)

    return result[0]


def test_mcp_server_copy_mode():
    """Тест COPY режима через MCP сервер."""

    print("\n" + "=" * 60)
    print("ТЕСТ: MCP сервер - COPY режим")
    print("=" * 60)

    # Создаём тестовый MD файл
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("""# Test Document

```mermaid
flowchart TD
    A[Start] --> B[End]
```

This is a test.
""")
        test_md = Path(f.name)

    # Создаём временную папку для результата
    output_dir = Path(tempfile.mkdtemp())

    try:
        # Формируем JSON-RPC запрос как это делает VS Code
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "convert_markdown_to_html",
                "arguments": {
                    "input_file": str(test_md),
                    "media_folder": str(test_md.parent),
                    "output_path": str(output_dir),
                    "media_mode": "copy",
                    "output_format": "html",
                    "validate_media": False,
                    "validate_mermaid": False,
                },
            },
        }

        # Запускаем MCP сервер и отправляем запрос
        print(f"\n📤 Отправляем JSON-RPC запрос...")
        print(f"   input_file: {test_md}")
        print(f"   output_path: {output_dir}")
        print(f"   media_mode: copy")

        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=Path(__file__).parent,
        )

        # MCP протокол требует инициализации
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        # Отправляем инициализацию
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Читаем ответ на инициализацию
        init_response = process.stdout.readline()
        print(f"   Инициализация: {init_response[:100]}")

        # Теперь отправляем настоящий запрос
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        process.stdin.close()

        # Читаем ответ построчно (JSON-RPC ответы идут построчно)
        response_line = process.stdout.readline()

        # Получили ответ - завершаем процесс
        process.terminate()

        # Читаем stderr для логов (неблокирующе)
        try:
            stderr = process.stderr.read()
        except:
            stderr = ""

        process.wait(timeout=5)

        print(f"\n📥 Получен ответ от MCP сервера")
        print(f"\n--- STDERR (логи) ---")
        print(stderr)

        print(f"\n--- STDOUT (JSON-RPC) ---")
        print(
            response_line[:500] + "..." if len(response_line) > 500 else response_line
        )

        # Парсим ответ
        try:
            # MCP возвращает вложенную структуру с content
            response = json.loads(response_line.strip())

            if "error" in response:
                print(f"\n❌ ОШИБКА: MCP вернул ошибку")
                print(f"   {response['error']}")
                return False

            # Извлекаем result.content[0].text и парсим как JSON
            mcp_result = response.get("result", {})
            content = mcp_result.get("content", [])

            if not content:
                print(f"\n❌ ОШИБКА: В result нет content")
                return False

            # content[0].text содержит JSON с нашим результатом
            result_text = content[0].get("text", "")
            result = json.loads(result_text)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"\n❌ ОШИБКА парсинга: {e}")
            print(f"   Первые 300 символов: {response_line[:300]}")
            return False

        # Проверяем что результат содержит нужные поля
        if result.get("status") != "success":
            print(f"\n❌ ОШИБКА: status != success")
            print(f"   Результат: {result}")
            return False

        # Проверяем что файлы созданы
        output_files = result.get("output_files", [])
        if not output_files:
            print(f"\n❌ ОШИБКА: Нет созданных файлов")
            return False

        html_file = Path(output_files[0])
        if not html_file.exists():
            print(f"\n❌ ОШИБКА: HTML файл не создан: {html_file}")
            return False

        # Проверяем что папка media создана
        media_dir = html_file.parent / "media"
        if not media_dir.exists():
            print(f"\n❌ ОШИБКА: Папка media не создана")
            return False

        # Проверяем что диаграмма отрендерена
        diagram_files = list(media_dir.glob("diagram_*.webp"))
        if not diagram_files:
            print(f"\n❌ ОШИБКА: Диаграммы не отрендерены в media/")
            return False

        print(f"\n✅ УСПЕХ!")
        print(f"   HTML создан: {html_file.name}")
        print(f"   Размер: {html_file.stat().st_size / 1024:.2f} KB")
        print(f"   Диаграмм отрендерено: {len(diagram_files)}")
        print(f"   Диаграммы: {[f.name for f in diagram_files]}")

        return True

    except subprocess.TimeoutExpired:
        print(f"\n❌ ОШИБКА: MCP сервер не ответил за 60 секунд (ЗАВИСАНИЕ)")
        process.kill()
        return False

    except Exception as e:
        print(f"\n❌ ИСКЛЮЧЕНИЕ: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Очистка
        test_md.unlink(missing_ok=True)


def test_mcp_server_embed_mode():
    """Тест EMBED режима через MCP сервер."""

    print("\n" + "=" * 60)
    print("ТЕСТ: MCP сервер - EMBED режим")
    print("=" * 60)

    # Создаём тестовый MD файл
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("""# Test Document

```mermaid
flowchart TD
    A[Start] --> B[End]
```

This is a test.
""")
        test_md = Path(f.name)

    # Создаём временную папку для результата
    output_dir = Path(tempfile.mkdtemp())

    try:
        # Формируем JSON-RPC запрос
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "convert_markdown_to_html",
                "arguments": {
                    "input_file": str(test_md),
                    "media_folder": str(test_md.parent),
                    "output_path": str(output_dir),
                    "media_mode": "embed",
                    "output_format": "html",
                    "validate_media": False,
                    "validate_mermaid": False,
                },
            },
        }

        print(f"\n📤 Отправляем JSON-RPC запрос...")
        print(f"   media_mode: embed")

        process = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=Path(__file__).parent,
        )

        # MCP протокол требует инициализации
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        }

        # Отправляем инициализацию
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()

        # Читаем ответ на инициализацию
        init_response = process.stdout.readline()

        # Отправляем настоящий запрос
        process.stdin.write(json.dumps(request) + "\n")
        process.stdin.flush()
        process.stdin.close()

        # Читаем ответ с таймаутом (EMBED может занимать до 2 минут)
        print(f"   ⏱️  Ожидание ответа (таймаут 120 секунд)...")
        response_line = read_with_timeout(process.stdout, timeout=120)

        if response_line is None:
            print(f"\n❌ ТАЙМАУТ: Сервер не ответил за 120 секунд (EMBED режим)")
            print(f"   Возможно Pandoc зависает на встраивании ресурсов")
            process.kill()
            return False

        # Получили ответ - завершаем процесс
        process.terminate()

        # Читаем stderr для логов (неблокирующе)
        try:
            stderr = process.stderr.read()
        except:
            stderr = ""

        process.wait(timeout=10)

        print(f"\n📥 Получен ответ от MCP сервера")
        print(f"\n--- STDERR (логи) ---")
        print(stderr)

        print(f"\n--- STDOUT (JSON-RPC) ---")
        print(
            response_line[:500] + "..." if len(response_line) > 500 else response_line
        )

        # Парсим ответ
        try:
            response = json.loads(response_line.strip())

            if "error" in response:
                print(f"\n❌ ОШИБКА: {response['error']}")
                return False

            # MCP возвращает вложенную структуру
            mcp_result = response.get("result", {})
            content = mcp_result.get("content", [])

            if not content:
                print(f"\n❌ ОШИБКА: В result нет content")
                return False

            result_text = content[0].get("text", "")
            result = json.loads(result_text)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"\n❌ ОШИБКА парсинга: {e}")
            print(f"   Первые 300 символов: {response_line[:300]}")
            return False

        if result.get("status") != "success":
            print(f"\n❌ ОШИБКА: status != success")
            return False

        # Проверяем что файл создан
        output_files = result.get("output_files", [])
        if not output_files:
            print(f"\n❌ ОШИБКА: Нет созданных файлов")
            return False

        html_file = Path(output_files[0])
        if not html_file.exists():
            print(f"\n❌ ОШИБКА: HTML файл не создан")
            return False

        # Проверяем что в HTML есть base64
        html_content = html_file.read_text(encoding="utf-8")
        if "data:image/webp;base64" not in html_content:
            print(f"\n❌ ОШИБКА: В HTML нет base64 встроенной диаграммы")
            return False

        print(f"\n✅ УСПЕХ!")
        print(f"   HTML создан: {html_file.name}")
        print(f"   Размер: {html_file.stat().st_size / 1024:.2f} KB")
        print(f"   Base64 диаграмма: ДА")

        return True

    except subprocess.TimeoutExpired:
        print(f"\n❌ ОШИБКА: MCP сервер не ответил за 60 секунд (ЗАВИСАНИЕ)")
        process.kill()
        return False

    except Exception as e:
        print(f"\n❌ ИСКЛЮЧЕНИЕ: {type(e).__name__}: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        test_md.unlink(missing_ok=True)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ИНТЕГРАЦИОННЫЕ ТЕСТЫ MCP СЕРВЕРА")
    print("=" * 60)

    results = []

    # Тест COPY режима
    results.append(("COPY режим", test_mcp_server_copy_mode()))

    # Тест EMBED режима
    results.append(("EMBED режим", test_mcp_server_embed_mode()))

    # Итоги
    print("\n" + "=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
        sys.exit(0)
    else:
        print("\n⚠️ ЕСТЬ ПРОВАЛИВШИЕСЯ ТЕСТЫ!")
        sys.exit(1)

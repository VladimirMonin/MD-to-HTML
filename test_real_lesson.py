#!/usr/bin/env python3
"""Тест MCP сервера с реальным контентом."""

import json
import subprocess
import sys
import threading
from pathlib import Path


def read_with_timeout(stream, timeout=60):
    """Чтение из stream с таймаутом."""
    result = [None]
    error = [None]

    def reader():
        try:
            result[0] = stream.readline()
        except Exception as e:
            error[0] = str(e)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    thread.join(timeout)

    if error[0]:
        raise Exception(error[0])
    if result[0] is None:
        raise TimeoutError(f"Не получен ответ за {timeout} сек")
    return result[0]


def test_real_lesson():
    """Тест с реальным файлом lesson_133."""

    print("=" * 60)
    print("ТЕСТ РЕАЛЬНОГО КОНТЕНТА: lesson_133_brief_results.md")
    print("=" * 60)
    print()

    # Параметры пользователя
    params = {
        "input_file": r"c:\Users\User\Documents\Syncthing\SK_OOP_COURSE\2_PART_UML\chapter_07\results\results\lesson_133_brief_results.md",
        "media_folder": r"c:\Users\User\Documents\Syncthing\SK_OOP_COURSE\2_PART_UML\chapter_07\media",
        "media_mode": "embed",
        "output_path": r"c:\Users\User\Documents\Syncthing\SK_OOP_COURSE\RELEASE\PART_02\CHAPTER_07",
        "enable_toc": True,
        "toc_depth": 2,
        "enable_breadcrumbs": True,
        "output_format": "html",
        "template": "web",
        "validate_media": True,
        "validate_mermaid": False,  # Отключена - двойная обработка
    }

    # Проверка файлов
    input_path = Path(params["input_file"])
    media_path = Path(params["media_folder"])
    output_path = Path(params["output_path"])

    print(f"📁 Входной файл: {input_path}")
    print(f"   Существует: {input_path.exists()}")
    if input_path.exists():
        size_mb = input_path.stat().st_size / 1024 / 1024
        print(f"   Размер: {size_mb:.2f} MB")

    print(f"\n📁 Папка медиа: {media_path}")
    print(f"   Существует: {media_path.exists()}")
    if media_path.exists():
        files = list(media_path.glob("*"))
        print(f"   Файлов: {len(files)}")

    print(f"\n📁 Выходная папка: {output_path}")
    print(f"   Существует: {output_path.exists()}")

    if not input_path.exists():
        print("\n❌ ВХОДНОЙ ФАЙЛ НЕ НАЙДЕН!")
        return

    if not media_path.exists():
        print("\n❌ ПАПКА МЕДИА НЕ НАЙДЕНА!")
        return

    print("\n" + "=" * 60)
    print("🚀 ЗАПУСК MCP СЕРВЕРА")
    print("=" * 60)
    print()

    # Запускаем сервер
    try:
        proc = subprocess.Popen(
            [sys.executable, "mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=Path(__file__).parent,
        )
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")
        return

    try:
        # Отправляем initialize
        print("📤 Инициализация MCP...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {}},
        }
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()

        # Читаем ответ
        init_response = read_with_timeout(proc.stdout, timeout=10)
        if init_response:
            print("✅ Initialize OK")
        else:
            print("❌ Нет ответа на initialize")
            return

        # Отправляем tool call
        print("\n📤 Отправляем запрос конвертации...")
        print(f"   Режим: {params['media_mode']}")
        print(f"   Формат: {params['output_format']}")

        tool_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "convert_markdown_to_html", "arguments": params},
        }

        import time

        start_time = time.time()

        proc.stdin.write(json.dumps(tool_request) + "\n")
        proc.stdin.flush()

        # Читаем результат с большим таймаутом (до 5 минут)
        print("\n⏱️  Ожидание ответа (максимум 300 сек)...")
        response = read_with_timeout(proc.stdout, timeout=300)

        elapsed = time.time() - start_time

        if response:
            result = json.loads(response)

            # Проверяем успех
            if "result" in result:
                content = result["result"]["content"][0]["text"]
                data = json.loads(content)

                if data.get("status") == "success":
                    print(f"\n✅ УСПЕХ! Время: {elapsed:.1f} сек")
                    print(f"\n📊 Результаты:")
                    print(f"   Выходные файлы: {len(data['output_files'])}")
                    for f in data["output_files"]:
                        file_path = Path(f)
                        if file_path.exists():
                            size_mb = file_path.stat().st_size / 1024 / 1024
                            print(f"   - {file_path.name} ({size_mb:.2f} MB)")

                    print(f"\n📈 Статистика:")
                    stats = data.get("stats", {})
                    print(f"   Медиа найдено: {stats.get('media_files_found', 0)}")
                    print(
                        f"   Медиа отсутствует: {stats.get('media_files_missing', 0)}"
                    )

                else:
                    print(f"\n❌ ОШИБКА: {data.get('message', 'Unknown error')}")
                    print(f"\nТип ошибки: {data.get('error_type')}")
                    if "details" in data and "traceback" in data["details"]:
                        print(f"\nТрассировка:")
                        print(data["details"]["traceback"][:500])
            else:
                print(f"\n❌ Ошибка протокола: {result}")
        else:
            print("❌ Нет ответа от сервера")

        # Читаем stderr логи
        print("\n" + "=" * 60)
        print("📋 ЛОГИ СЕРВЕРА (stderr)")
        print("=" * 60)

        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()

        stderr = proc.stderr.read()
        if stderr:
            # Выводим последние 50 строк логов
            lines = stderr.split("\n")
            for line in lines[-50:]:
                if line.strip():
                    print(line)

    except TimeoutError as e:
        print(f"\n❌ TIMEOUT: {e}")
        proc.terminate()
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        proc.terminate()


if __name__ == "__main__":
    test_real_lesson()

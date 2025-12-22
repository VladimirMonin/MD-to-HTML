@echo off
REM Запуск MD-to-HTML GUI через виртуальное окружение
chcp 65001 >nul
title MD-to-HTML Converter GUI

echo.
echo ===============================================
echo   MD-to-HTML Converter - GUI Launcher
echo ===============================================
echo.

REM Проверка существования виртуального окружения
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo.
    echo Пожалуйста, создайте виртуальное окружение:
    echo   poetry install
    echo.
    echo Или:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Проверка существования gui_app.py
if not exist "gui_app.py" (
    echo [ERROR] Файл gui_app.py не найден!
    echo.
    echo Убедитесь, что вы запускаете скрипт из корневой папки проекта.
    echo.
    pause
    exit /b 1
)

echo [INFO] Запуск GUI приложения...
echo.

REM Запуск GUI через виртуальное окружение
".venv\Scripts\python.exe" gui_app.py

REM Проверка кода возврата
if %ERRORLEVEL% neq 0 (
    echo.
    echo ===============================================
    echo [ERROR] Приложение завершилось с ошибкой!
    echo Код ошибки: %ERRORLEVEL%
    echo ===============================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

REM Успешное завершение (без паузы, чтобы окно закрылось)
exit /b 0

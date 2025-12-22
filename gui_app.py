#!/usr/bin/env python3
"""
Запуск GUI приложения MD-to-HTML конвертера.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# Добавляем путь к модулям проекта
sys.path.insert(0, str(Path(__file__).parent))

from gui import MainWindow


def main():
    """Точка входа в GUI приложение."""
    # Включаем высокое DPI разрешение
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("MD-to-HTML Converter")
    app.setOrganizationName("MD-Converter")

    # Создание и показ главного окна
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

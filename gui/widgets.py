"""
Кастомные виджеты для GUI.
Drop-зоны для перетаскивания файлов и папок.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DropZone(QFrame):
    """Зона для перетаскивания файлов/папок."""

    # Сигнал испускается когда путь изменился
    pathChanged = pyqtSignal(str)

    def __init__(
        self, label: str, accept_dirs: bool = True, accept_files: bool = False
    ):
        """
        Args:
            label: Текст метки
            accept_dirs: Принимать папки
            accept_files: Принимать файлы
        """
        super().__init__()
        self.accept_dirs = accept_dirs
        self.accept_files = accept_files
        self._current_path = ""
        self.is_dark = True

        self.setAcceptDrops(True)
        self.setup_ui(label)
        self.apply_styles()

    def setup_ui(self, label: str):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок
        self.title_label = QLabel(label)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Путь
        self.path_label = QLabel("Перетащите сюда папку или файл")
        self.path_label.setWordWrap(True)
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.title_label)
        layout.addWidget(self.path_label)

    def apply_styles(self, is_dark: Optional[bool] = None):
        """Применение стилей."""
        if is_dark is not None:
            self.is_dark = is_dark

        if self.is_dark:
            self.setStyleSheet("""
                DropZone {
                    border: 2px dashed #555;
                    border-radius: 8px;
                    background-color: #2b2b2b;
                }
                DropZone:hover {
                    border-color: #0078d4;
                    background-color: #333;
                }
            """)
            self.title_label.setStyleSheet(
                "font-weight: bold; font-size: 11pt; color: #e0e0e0;"
            )
            self.path_label.setStyleSheet("color: #888; font-size: 9pt;")
        else:
            self.setStyleSheet("""
                DropZone {
                    border: 2px dashed #ccc;
                    border-radius: 8px;
                    background-color: #f9f9f9;
                }
                DropZone:hover {
                    border-color: #0078d4;
                    background-color: #f0f7ff;
                }
            """)
            self.title_label.setStyleSheet(
                "font-weight: bold; font-size: 11pt; color: #1a1a1a;"
            )
            self.path_label.setStyleSheet("color: #666; font-size: 9pt;")

        self.setMinimumHeight(100)

    def dragEnterEvent(self, event: Optional[QDragEnterEvent]):
        """Обработка входа перетаскиваемого объекта."""
        if event is None:
            return

        mime_data = event.mimeData()
        if mime_data and mime_data.hasUrls():
            event.acceptProposedAction()

            # Подсветка при наведении
            if self.is_dark:
                self.setStyleSheet("""
                    DropZone {
                        border: 2px solid #0078d4;
                        border-radius: 8px;
                        background-color: #1a4d7a;
                    }
                """)
            else:
                self.setStyleSheet("""
                    DropZone {
                        border: 2px solid #0078d4;
                        border-radius: 8px;
                        background-color: #e1f0ff;
                    }
                """)

    def dragLeaveEvent(self, event):
        """Обработка выхода перетаскиваемого объекта."""
        self.apply_styles()

    def dropEvent(self, event: Optional[QDropEvent]):
        """Обработка сброса файла/папки."""
        if event is None:
            return

        self.apply_styles()

        mime_data = event.mimeData()
        if not mime_data:
            return

        urls = mime_data.urls()
        if not urls:
            return

        path = Path(urls[0].toLocalFile())

        # Проверка типа
        error_color = "#ff5555" if self.is_dark else "#d73a49"
        if path.is_dir() and not self.accept_dirs:
            self.path_label.setText("❌ Принимаются только файлы")
            self.path_label.setStyleSheet(f"color: {error_color}; font-size: 9pt;")
            return

        if path.is_file() and not self.accept_files:
            self.path_label.setText("❌ Принимаются только папки")
            self.path_label.setStyleSheet(f"color: {error_color}; font-size: 9pt;")
            return

        if not path.exists():
            self.path_label.setText("❌ Путь не существует")
            self.path_label.setStyleSheet(f"color: {error_color}; font-size: 9pt;")
            return

        # Установка пути
        self.set_path(str(path))
        event.acceptProposedAction()

    def set_path(self, path: str):
        """
        Установка пути программно.

        Args:
            path: Новый путь
        """
        self._current_path = path
        display_path = path if len(path) < 60 else "..." + path[-57:]
        self.path_label.setText(f"📁 {display_path}")

        # Цвет текста при установленном пути
        color = "#50fa7b" if self.is_dark else "#28a745"
        self.path_label.setStyleSheet(
            f"color: {color}; font-size: 9pt; font-weight: bold;"
        )
        self.pathChanged.emit(path)

    def get_path(self) -> str:
        """Получение текущего пути."""
        return self._current_path

    def clear(self):
        """Очистка пути."""
        self._current_path = ""
        self.path_label.setText("Перетащите сюда папку или файл")
        color = "#888" if self.is_dark else "#666"
        self.path_label.setStyleSheet(f"color: {color}; font-size: 9pt;")


class InputDropZone(DropZone):
    """Drop-зона для входного MD файла или папки."""

    def __init__(self):
        super().__init__(
            label="📄 Входной файл/папка", accept_dirs=True, accept_files=True
        )

    def dropEvent(self, event: Optional[QDropEvent]):
        """Переопределение для проверки MD файлов."""
        if event is None:
            return

        self.apply_styles()

        mime_data = event.mimeData()
        if not mime_data:
            return

        urls = mime_data.urls()
        if not urls:
            return

        path = Path(urls[0].toLocalFile())

        # Проверка для файлов - должен быть .md
        if path.is_file() and path.suffix.lower() != ".md":
            self.path_label.setText("❌ Принимаются только .md файлы или папки")
            self.path_label.setStyleSheet("color: #ff5555; font-size: 9pt;")
            return

        if not path.exists():
            self.path_label.setText("❌ Путь не существует")
            self.path_label.setStyleSheet("color: #ff5555; font-size: 9pt;")
            return

        # Установка пути
        self.set_path(str(path))
        event.acceptProposedAction()

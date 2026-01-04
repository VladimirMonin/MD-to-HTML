"""
Главное окно приложения MD-to-HTML GUI.
"""

import copy
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QGroupBox,
    QCheckBox,
    QTextEdit,
    QMessageBox,
    QProgressBar,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from .widgets import DropZone, InputDropZone
from .config_manager import ConfigManager


class ConversionWorker(QThread):
    """Рабочий поток для конвертации."""

    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(str)  # status message

    def __init__(self, config: dict, input_path: str):
        super().__init__()
        self.config = copy.deepcopy(config)
        self.input_path = input_path

    def run(self):
        """Выполнение конвертации."""
        try:
            from md_converter import Converter, ConverterConfig

            self.progress.emit("📝 Подготовка конфигурации...")

            # Удаляем лишние ключи которых нет в схеме ConverterConfig
            clean_config = {k: v for k, v in self.config.items() if k != "theme"}
            
            # DEBUG: проверяем что styles передается
            print(f"🔍 DEBUG: styles в конфиге = {clean_config.get('styles', 'ОТСУТСТВУЕТ')}")

            # Создание конфигурации
            converter_config = ConverterConfig.from_dict(clean_config)
            
            # DEBUG: проверяем что тема применилась
            print(f"🔍 DEBUG: mermaid_theme в ConverterConfig = {converter_config.styles.mermaid_theme}")
            converter = Converter(converter_config)

            self.progress.emit("🔄 Конвертация...")

            # Конвертация - возвращает list[Path]
            results = converter.convert(self.input_path)

            # Формирование сообщения
            output_files = []
            for path in results:
                if path and path.exists():
                    output_files.append(f"  • {path.suffix.upper()[1:]}: {path}")

            message = "✅ Конвертация завершена!\n\n" + "\n".join(output_files)
            self.finished.emit(True, message)

        except Exception as e:
            self.finished.emit(False, f"❌ Ошибка: {str(e)}")


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.current_settings = copy.deepcopy(self.config_manager.get_all())
        self.worker: Optional[ConversionWorker] = None

        # Загрузка темы из конфига
        saved_theme = self.current_settings.get("theme", "dark")
        self.dark_theme = saved_theme == "dark"

        self.setWindowTitle("MD-to-HTML Converter v2.0")
        self.setMinimumSize(850, 1150)
        self.resize(850, 1150)

        self.setup_ui()
        self.load_settings_to_ui()
        self.apply_theme()  # Применяем тему после создания UI

    def setup_ui(self):
        """Создание интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title = QLabel("📚 MD-to-HTML Converter")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        # === ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ ===
        theme_layout = QHBoxLayout()
        theme_layout.addStretch()
        self.theme_btn = QPushButton("☀️ Светлая тема")
        self.theme_btn.setMaximumWidth(150)
        self.theme_btn.clicked.connect(self.toggle_theme)
        theme_layout.addWidget(self.theme_btn)
        main_layout.addLayout(theme_layout)

        # === ИСТОЧНИК ССЫЛОК ===
        source_group = QGroupBox("🔗 Формат исходных ссылок")
        source_layout = QVBoxLayout(source_group)

        self.source_type_combo = QComboBox()
        self.source_type_combo.addItems(["Obsidian", "Standard"])
        self.source_type_combo.currentTextChanged.connect(self.on_source_type_changed)
        source_layout.addWidget(QLabel("Тип ресурса:"))
        source_layout.addWidget(self.source_type_combo)

        main_layout.addWidget(source_group)

        # === DROP ЗОНЫ ===
        # Входной файл
        self.input_drop = InputDropZone()
        self.input_drop.pathChanged.connect(self.on_input_path_changed)
        main_layout.addWidget(self.input_drop)

        # Папка с медиа
        self.media_drop = DropZone(
            "📁 Папка с медиа-файлами", accept_dirs=True, accept_files=False
        )
        self.media_drop.pathChanged.connect(self.on_media_folder_changed)
        main_layout.addWidget(self.media_drop)

        # Папка вывода
        self.output_drop = DropZone(
            "📂 Папка вывода (output_dir)", accept_dirs=True, accept_files=False
        )
        self.output_drop.pathChanged.connect(self.on_output_dir_changed)
        main_layout.addWidget(self.output_drop)

        # === ФОРМАТЫ ВЫВОДА ===
        format_group = QGroupBox("📦 Выходные форматы")
        format_layout = QVBoxLayout(format_group)

        format_row = QHBoxLayout()
        self.html_check = QCheckBox("HTML")
        self.html_check.setChecked(True)
        self.html_check.stateChanged.connect(self.on_format_changed)

        self.epub_check = QCheckBox("EPUB")
        self.epub_check.stateChanged.connect(self.on_format_changed)

        format_row.addWidget(self.html_check)
        format_row.addWidget(self.epub_check)
        format_row.addStretch()
        format_layout.addLayout(format_row)

        main_layout.addWidget(format_group)

        # === ПАРАМЕТРЫ ===
        params_group = QGroupBox("⚙️ Параметры")
        params_layout = QVBoxLayout(params_group)

        # Шаблон
        template_row = QHBoxLayout()
        template_row.addWidget(QLabel("Шаблон:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(["book", "web"])
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_row.addWidget(self.template_combo)
        template_row.addStretch()
        params_layout.addLayout(template_row)

        # Режим медиа
        media_row = QHBoxLayout()
        media_row.addWidget(QLabel("Медиа:"))
        self.media_mode_combo = QComboBox()
        self.media_mode_combo.addItems(["embed", "copy"])
        self.media_mode_combo.currentTextChanged.connect(self.on_media_mode_changed)
        media_row.addWidget(self.media_mode_combo)
        media_row.addStretch()
        params_layout.addLayout(media_row)

        # Фичи
        features_label = QLabel("Функции:")
        features_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        params_layout.addWidget(features_label)

        features_layout = QVBoxLayout()
        features_layout.setSpacing(5)

        self.toc_check = QCheckBox("Оглавление (TOC)")
        self.breadcrumbs_check = QCheckBox("Хлебные крошки")
        self.code_copy_check = QCheckBox("Копирование кода")
        self.mermaid_check = QCheckBox("Диаграммы Mermaid")
        self.callouts_check = QCheckBox("Callout блоки")

        for checkbox in [
            self.toc_check,
            self.breadcrumbs_check,
            self.code_copy_check,
            self.mermaid_check,
            self.callouts_check,
        ]:
            checkbox.stateChanged.connect(self.on_feature_changed)
            features_layout.addWidget(checkbox)

        params_layout.addLayout(features_layout)
        main_layout.addWidget(params_group)

        # === ЛОГ ===
        log_label = QLabel("📋 Статус:")
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        self.log_text.setPlaceholderText("Здесь будет отображаться статус операций...")
        main_layout.addWidget(self.log_text)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # === КНОПКИ ===
        buttons_layout = QHBoxLayout()

        self.convert_btn = QPushButton("🚀 Сгенерировать")
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setObjectName("convert_btn")
        self.convert_btn.clicked.connect(self.on_convert_clicked)

        self.save_btn = QPushButton("💾 Сохранить настройки")
        self.save_btn.setMinimumHeight(50)
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.on_save_clicked)

        buttons_layout.addWidget(self.convert_btn)
        buttons_layout.addWidget(self.save_btn)

        main_layout.addLayout(buttons_layout)

    def load_settings_to_ui(self):
        """Загрузка настроек из config в UI."""
        config = self.current_settings

        # Source type
        source = config.get("input", {}).get("source_type", "obsidian")
        self.source_type_combo.setCurrentText(source.capitalize())

        # Paths - ВАЖНО: загружаем входной путь тоже!
        input_path = config.get("input", {}).get("path", "")
        if input_path:
            self.input_drop.set_path(input_path)

        files_folder = config.get("input", {}).get("files_folder", "")
        if files_folder:
            self.media_drop.set_path(files_folder)

        output_dir = config.get("output_dir", "./build")
        if output_dir:
            self.output_drop.set_path(output_dir)

        # Formats
        formats = config.get("formats", ["html"])
        self.html_check.setChecked("html" in formats)
        self.epub_check.setChecked("epub" in formats)

        # Template
        template = config.get("template", "book")
        self.template_combo.setCurrentText(template)

        # Media mode
        media_mode = config.get("media_mode", "embed")
        self.media_mode_combo.setCurrentText(media_mode)

        # Features - БЛОКИРУЕМ СИГНАЛЫ чтобы не триггерить on_feature_changed
        features = config.get("features", {})
        for checkbox in [
            self.toc_check,
            self.breadcrumbs_check,
            self.code_copy_check,
            self.mermaid_check,
            self.callouts_check,
        ]:
            checkbox.blockSignals(True)

        self.toc_check.setChecked(features.get("toc", True))
        self.breadcrumbs_check.setChecked(features.get("breadcrumbs", True))
        self.code_copy_check.setChecked(features.get("code_copy", True))
        self.mermaid_check.setChecked(features.get("mermaid", True))
        self.callouts_check.setChecked(features.get("callouts", True))

        for checkbox in [
            self.toc_check,
            self.breadcrumbs_check,
            self.code_copy_check,
            self.mermaid_check,
            self.callouts_check,
        ]:
            checkbox.blockSignals(False)

        self.log("✅ Настройки загружены из config.yaml")

    def on_source_type_changed(self, text: str):
        """Изменение типа источника."""
        self.current_settings.setdefault("input", {})["source_type"] = text.lower()
        self.log(f"🔗 Тип ресурса изменен: {text}")

    def on_input_path_changed(self, path: str):
        """Изменение входного пути."""
        self.current_settings.setdefault("input", {})["path"] = path
        self.log(f"📄 Входной путь: {path}")

    def on_media_folder_changed(self, path: str):
        """Изменение папки с медиа."""
        self.current_settings.setdefault("input", {})["files_folder"] = path
        self.log(f"📁 Папка медиа: {path}")

    def on_output_dir_changed(self, path: str):
        """Изменение папки вывода."""
        self.current_settings["output_dir"] = path
        self.log(f"📂 Папка вывода: {path}")

    def on_format_changed(self):
        """Изменение форматов вывода."""
        formats = []
        if self.html_check.isChecked():
            formats.append("html")
        if self.epub_check.isChecked():
            formats.append("epub")

        self.current_settings["formats"] = formats
        self.log(f"📦 Форматы: {', '.join(formats).upper()}")

    def on_template_changed(self, text: str):
        """Изменение шаблона."""
        self.current_settings["template"] = text
        self.log(f"🎨 Шаблон: {text}")

    def on_media_mode_changed(self, text: str):
        """Изменение режима медиа."""
        self.current_settings["media_mode"] = text
        self.log(f"🖼️ Режим медиа: {text}")

    def on_feature_changed(self):
        """Изменение функций."""
        if "features" not in self.current_settings:
            self.current_settings["features"] = {}

        # Обновляем только те фичи, которые есть в GUI
        # Остальные (fullscreen, plyr и т.д.) сохраняются из конфига благодаря deepcopy
        features = self.current_settings["features"]
        features["toc"] = self.toc_check.isChecked()
        features["breadcrumbs"] = self.breadcrumbs_check.isChecked()
        features["code_copy"] = self.code_copy_check.isChecked()
        features["mermaid"] = self.mermaid_check.isChecked()
        features["callouts"] = self.callouts_check.isChecked()

    def on_save_clicked(self):
        """Сохранение настроек в config.yaml."""
        try:
            # Загружаем актуальный конфиг с диска
            self.config_manager.load()

            # Обновляем его нашими текущими настройками из UI
            # deep_update в ConfigManager позаботится о сохранении вложенных полей
            self.config_manager.update(self.current_settings)
            self.config_manager.save()

            self.log("💾 Настройки сохранены в config.yaml")
            QMessageBox.information(self, "Успех", "✅ Настройки успешно сохранены!")
        except Exception as e:
            self.log(f"❌ Ошибка сохранения: {e}")
            QMessageBox.critical(
                self, "Ошибка", f"❌ Не удалось сохранить настройки:\n{e}"
            )

    def on_convert_clicked(self):
        """Запуск конвертации."""
        # Проверка входного пути
        input_path = self.current_settings.get("input", {}).get("path", "")
        if not input_path:
            input_path = self.input_drop.get_path()

        if not input_path:
            QMessageBox.warning(self, "Внимание", "⚠️ Укажите входной файл или папку!")
            return

        # Проверка форматов
        if not self.current_settings.get("formats"):
            QMessageBox.warning(
                self, "Внимание", "⚠️ Выберите хотя бы один выходной формат!"
            )
            return

        # Запуск конвертации
        self.log("🚀 Начало конвертации...")
        self.convert_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Бесконечный прогресс

        self.worker = ConversionWorker(self.current_settings, input_path)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.on_conversion_finished)
        self.worker.start()

    def on_conversion_finished(self, success: bool, message: str):
        """Завершение конвертации."""
        self.log(message)
        self.convert_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

        if success:
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)

    def log(self, message: str):
        """Добавление сообщения в лог."""
        self.log_text.append(message)
        # Прокрутка вниз
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def toggle_theme(self):
        """Переключение темы."""
        self.dark_theme = not self.dark_theme
        self.current_settings["theme"] = "dark" if self.dark_theme else "light"
        self.apply_theme()
        self.log(f"🎨 Тема изменена: {'темная' if self.dark_theme else 'светлая'}")

    def apply_theme(self):
        """Применение выбранной темы."""
        if self.dark_theme:
            self.apply_dark_theme()
            self.theme_btn.setText("☀️ Светлая тема")
        else:
            self.apply_light_theme()
            self.theme_btn.setText("🌙 Темная тема")

        # Обновляем стили drop-зон
        for widget in [self.input_drop, self.media_drop, self.output_drop]:
            widget.apply_styles(self.dark_theme)

    def apply_light_theme(self):
        """Применение светлой темы."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #1a1a1a;
            }
            QGroupBox {
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #0078d4;
            }
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 6px 10px;
                color: #1a1a1a;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                border: 1px solid #0078d4;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
            }
            QCheckBox {
                spacing: 8px;
                padding: 5px;
                font-size: 11pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #ccc;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
                color: #1a1a1a;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 10pt;
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
                text-align: center;
                color: #1a1a1a;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QPushButton#convert_btn {
                background-color: #0078d4;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#convert_btn:hover {
                background-color: #005a9e;
            }
            QPushButton#convert_btn:disabled {
                background-color: #ccc;
                color: #888;
            }
            QPushButton#save_btn {
                background-color: #28a745;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#save_btn:hover {
                background-color: #218838;
            }
        """)

    def apply_dark_theme(self):
        """Применение темной темы."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QGroupBox {
                border: 1px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 10px;
                font-weight: bold;
                background-color: #252526;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #0078d4;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px 10px;
                color: #e0e0e0;
                min-height: 25px;
            }
            QComboBox:hover {
                border-color: #0078d4;
            }
            QComboBox QAbstractItemView {
                background-color: #2b2b2b;
                border: 1px solid #0078d4;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                color: #e0e0e0;
            }
            QCheckBox {
                spacing: 8px;
                padding: 5px;
                font-size: 11pt;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                background-color: #0078d4;
                border-color: #0078d4;
            }
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px;
                color: #d4d4d4;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #2b2b2b;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
            }
            QPushButton#convert_btn {
                background-color: #0078d4;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#convert_btn:hover {
                background-color: #005a9e;
            }
            QPushButton#convert_btn:disabled {
                background-color: #444;
                color: #888;
            }
            QPushButton#save_btn {
                background-color: #28a745;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#save_btn:hover {
                background-color: #218838;
            }
        """)

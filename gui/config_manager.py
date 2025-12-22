"""
Менеджер конфигурации для GUI.
Чтение и запись config.yaml.
"""

from pathlib import Path
from typing import Dict, Any
import yaml


class ConfigManager:
    """Управление конфигурацией приложения."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Args:
            config_path: Путь к файлу конфигурации
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Загрузка конфигурации из YAML."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Конфигурация не найдена: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        return self.config

    def save(self) -> None:
        """Сохранение конфигурации в YAML."""
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(
                self.config,
                f,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Получение значения из конфигурации.

        Args:
            key: Ключ (поддерживает точечную нотацию, например 'input.path')
            default: Значение по умолчанию
        """
        keys = key.split(".")
        value: Any = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Установка значения в конфигурации.

        Args:
            key: Ключ (поддерживает точечную нотацию)
            value: Новое значение
        """
        keys = key.split(".")
        config = self.config

        # Навигация по вложенным ключам
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Установка значения
        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """Получение всей конфигурации."""
        return self.config.copy()

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Обновление конфигурации из словаря.

        Args:
            updates: Словарь с обновлениями
        """

        def deep_update(base: dict, updates: dict) -> None:
            for key, value in updates.items():
                if (
                    isinstance(value, dict)
                    and key in base
                    and isinstance(base[key], dict)
                ):
                    deep_update(base[key], value)
                else:
                    base[key] = value

        deep_update(self.config, updates)

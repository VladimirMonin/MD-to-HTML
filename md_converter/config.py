"""Конфигурация конвертера MD-to-HTML."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import yaml


@dataclass
class InputConfig:
    """Настройки входных данных."""

    path: str = ""
    source_type: str = "standard"  # obsidian | standard
    files_folder: str = ""


@dataclass
class MetadataConfig:
    """Метаданные документа."""

    title: str = ""
    author: str = ""
    lang: str = "ru"
    brand_image: str = ""


@dataclass
class StylesConfig:
    """Настройки стилей."""

    highlight_theme: str = "github-dark"
    mermaid_theme: str = "neutral"


@dataclass
class FontsConfig:
    """Настройки шрифтов для EPUB."""

    embed: bool = True
    dir: str = "assets/fonts"


@dataclass
class FeaturesConfig:
    """Включение/отключение функций."""

    toc: bool = True
    toc_depth: int = 2
    breadcrumbs: bool = True
    code_copy: bool = True
    fullscreen: bool = True
    diff_blocks: bool = True
    callouts: bool = True
    mermaid: bool = True
    plyr: bool = True


@dataclass
class AdvancedConfig:
    """Продвинутые настройки."""

    pandoc_extra_args: list[str] = field(default_factory=list)
    custom_css: list[str] = field(default_factory=list)
    custom_js: list[str] = field(default_factory=list)


@dataclass
class ConverterConfig:
    """Главная конфигурация конвертера."""

    output_dir: str = "./build"
    template: Literal["book", "web"] = "book"
    media_mode: Literal["embed", "copy"] = "embed"
    formats: list[str] = field(default_factory=lambda: ["html"])

    input: InputConfig = field(default_factory=InputConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    styles: StylesConfig = field(default_factory=StylesConfig)
    fonts: FontsConfig = field(default_factory=FontsConfig)
    features: FeaturesConfig = field(default_factory=FeaturesConfig)
    advanced: AdvancedConfig = field(default_factory=AdvancedConfig)

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ConverterConfig":
        """Загрузка конфигурации из YAML файла."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict) -> "ConverterConfig":
        """Создание конфигурации из словаря."""
        return cls(
            output_dir=data.get("output_dir", "./build"),
            template=data.get("template", "book"),
            media_mode=data.get("media_mode", "embed"),
            formats=data.get("formats", ["html"]),
            input=InputConfig(**data.get("input", {})),
            metadata=MetadataConfig(**data.get("metadata", {})),
            styles=StylesConfig(**data.get("styles", {})),
            fonts=FontsConfig(**data.get("fonts", {})),
            features=FeaturesConfig(**data.get("features", {})),
            advanced=AdvancedConfig(**data.get("advanced", {})),
        )

    def merge_cli_args(self, **kwargs) -> "ConverterConfig":
        """
        Переопределение настроек из CLI аргументов.
        CLI args имеют приоритет над YAML.
        """
        for key, value in kwargs.items():
            if value is not None and hasattr(self, key):
                setattr(self, key, value)
        return self

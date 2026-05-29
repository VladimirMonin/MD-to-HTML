"""Регрессионные проверки CSS/JS раскладки статических Mermaid-изображений."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INTERACTIVE_CSS = PROJECT_ROOT / "assets" / "css" / "modules" / "interactive.css"
FULLSCREEN_JS = PROJECT_ROOT / "assets" / "js" / "modules" / "fullscreen.js"


def test_mermaid_static_images_reset_global_min_width() -> None:
    """Высокие Mermaid-картинки не должны наследовать базовый img min-width: 60%."""
    css = INTERACTIVE_CSS.read_text(encoding="utf-8")

    assert 'img[alt*="Mermaid Diagram"]' in css
    mermaid_block = css.split('img[alt*="Mermaid Diagram"] {', 1)[1].split("}", 1)[0]

    assert "min-width: 0;" in mermaid_block
    assert "height: auto;" in mermaid_block
    assert "object-fit: contain;" in mermaid_block


def test_mermaid_layout_has_portrait_and_wide_modes() -> None:
    """Для портретных и широких диаграмм есть отдельные preview-режимы."""
    css = INTERACTIVE_CSS.read_text(encoding="utf-8")
    js = FULLSCREEN_JS.read_text(encoding="utf-8")

    assert "mermaid-diagram--portrait" in css
    assert "mermaid-diagram--wide" in css
    assert 'figure:has(img[alt*="Mermaid Diagram"].mermaid-diagram--portrait)' in css
    assert "overflow-y: auto;" in css
    assert "width: min(100%, 760px);" in css
    assert "width: min(100%, 1200px);" in css
    assert "function classifyMermaidImage" in js
    assert "naturalWidth" in js
    assert "naturalHeight" in js

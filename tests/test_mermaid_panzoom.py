"""Tests for opt-in copy-mode Mermaid SVG pan/zoom."""

import pytest

from md_converter import Converter, ConverterConfig
from md_converter.preprocessors import MermaidPreprocessor
from md_converter.processors import TemplateProcessor
from md_converter.config import FeaturesConfig, StylesConfig


MERMAID_MD = """# Diagram

```mermaid
graph TD
    A[Start] --> B[Finish]
```
"""


SVG_WITH_XSS = """<svg width="100" height="80" onload="alert(1)">
<script>alert(1)</script>
<a href="javascript:alert(2)"><text>unsafe</text></a>
<g onclick="alert(3)"><text>safe label</text></g>
</svg>"""


def test_config_default_keeps_mermaid_panzoom_disabled() -> None:
    config = ConverterConfig()

    assert config.media_mode == "embed"
    assert config.features.mermaid_panzoom is False


def test_embed_panzoom_is_rejected_to_preserve_single_file_contract() -> None:
    config = ConverterConfig()
    config.media_mode = "embed"
    config.features.mermaid_panzoom = True

    with pytest.raises(ValueError, match="media_mode='copy'"):
        Converter(config)


def test_epub_panzoom_is_rejected_to_preserve_epub_behavior() -> None:
    config = ConverterConfig()
    config.media_mode = "copy"
    config.formats = ["html", "epub"]
    config.features.mermaid_panzoom = True

    with pytest.raises(ValueError, match="HTML output only"):
        Converter(config)


def test_copy_static_mermaid_still_renders_webp(monkeypatch, tmp_path) -> None:
    config = ConverterConfig()
    config.media_mode = "copy"
    config.output_dir = str(tmp_path)
    config.features.mermaid_panzoom = False
    preprocessor = MermaidPreprocessor(config, format_type="html")

    monkeypatch.setattr(preprocessor, "_render_diagram", lambda _code, _idx: b"webp-bytes")

    result = preprocessor.process(MERMAID_MD)

    assert "mermaid-panzoom-shell" not in result
    assert "![Mermaid Diagram 1](media/diagram_1.webp)" in result
    assert (tmp_path / "media" / "diagram_1.webp").read_bytes() == b"webp-bytes"


def test_copy_panzoom_mermaid_emits_svg_shell_and_no_webp(monkeypatch, tmp_path) -> None:
    config = ConverterConfig()
    config.media_mode = "copy"
    config.output_dir = str(tmp_path)
    config.features.mermaid_panzoom = True
    preprocessor = MermaidPreprocessor(config, format_type="html")

    monkeypatch.setattr(preprocessor, "_render_diagram_svg", lambda _code, _idx: "<svg><text>ok</text></svg>")

    result = preprocessor.process(MERMAID_MD)

    assert 'class="mermaid-panzoom-shell"' in result
    assert 'class="mermaid-toolbar"' in result
    assert 'class="mermaid-viewport"' in result
    assert '<script type="text/plain" class="mermaid-source" data-diagram="1">' in result
    assert "<svg><text>ok</text></svg>" in result
    assert "data:image/webp" not in result
    assert "diagram_1.webp" not in result
    assert not (tmp_path / "media" / "diagram_1.webp").exists()


def test_mermaid_source_debug_block_escapes_untrusted_source() -> None:
    preprocessor = MermaidPreprocessor(format_type="html")

    block = preprocessor._source_debug_block(
        "graph TD\nA[</script><script>alert(1)</script>]",
        "graph TD\nA[</script><script>alert(1)</script>]",
        1,
    )

    assert "</script><script>" not in block
    assert "&lt;/script&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in block


def test_svg_sanitizer_strips_scripts_events_and_javascript_urls() -> None:
    preprocessor = MermaidPreprocessor(format_type="html")

    sanitized = preprocessor._sanitize_svg(SVG_WITH_XSS)

    assert "<script" not in sanitized.lower()
    assert "onload" not in sanitized.lower()
    assert "onclick" not in sanitized.lower()
    assert "javascript:" not in sanitized.lower()
    assert 'preserveAspectRatio="xMidYMid meet"' in sanitized
    assert "safe label" in sanitized


def test_template_includes_panzoom_assets_only_for_copy_panzoom() -> None:
    features = FeaturesConfig(mermaid_panzoom=True)
    copy_header = TemplateProcessor(
        "web",
        features,
        StylesConfig(),
        media_mode="copy",
    ).build_header("html")
    embed_header = TemplateProcessor(
        "web",
        features,
        StylesConfig(),
        media_mode="embed",
    ).build_header("html")

    assert "assets/css/modules/mermaid-panzoom.css" in copy_header
    assert "function initMermaidPanZoom" in copy_header
    assert "assets/css/modules/mermaid-panzoom.css" not in embed_header
    assert "function initMermaidPanZoom" not in embed_header

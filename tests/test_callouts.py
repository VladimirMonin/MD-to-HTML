"""Tests for Obsidian callout DOM contract."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

from md_converter import Converter, ConverterConfig
from md_converter.preprocessors.callouts import CalloutsPreprocessor


class _TagCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag, dict(attrs)))

    def count_by_class(self, class_name: str) -> int:
        return sum(
            1
            for _, attrs in self.tags
            if class_name in (attrs.get("class") or "").split()
        )

    def count_by_attr(self, attr_name: str) -> int:
        return sum(1 for _, attrs in self.tags if attr_name in attrs)

    def classes_with_attr(self, attr_name: str) -> list[str]:
        return [attrs.get("class") or "" for _, attrs in self.tags if attr_name in attrs]


def _render_callout_fixture(tmp_path: Path) -> str:
    note = tmp_path / "callouts.md"
    note.write_text(
        """# Callouts

> [!NOTE] Note title
> Body with **bold** and `code`.
>
> - first item
> - second item

> [!WARNING] Warning title
> Warning body.

> [!QUESTION] Question title
> Question body.

> [!IMPORTANT] Important title
> Important body.
""",
        encoding="utf-8",
    )

    config = ConverterConfig()
    config.formats = ["html"]
    config.media_mode = "copy"
    config.output_dir = str(tmp_path / "build")
    config.features.mermaid = False
    config.features.toc = False
    config.features.breadcrumbs = False
    config.features.timecodes = False
    config.metadata.title = "Callouts"

    output = Converter(config).convert(note, "callouts")[0]
    return output.read_text(encoding="utf-8")


def test_callouts_preprocessor_emits_stable_contract_and_preserves_markdown_body():
    processed = CalloutsPreprocessor().process(
        """> [!WARNING] Careful <unsafe>
> Body with **bold**, `code`, and a list.
>
> - item
"""
    )

    assert '::: {.callout .callout-warning .warning data-callout="warning"}' in processed
    assert '::: {.callout-title}' in processed
    assert 'class="callout-icon"' in processed
    assert 'class="callout-title-text">Careful &lt;unsafe&gt;</span>' in processed
    assert '::: {.callout-body}' in processed
    assert "Body with **bold**, `code`, and a list." in processed
    assert "- item" in processed


def test_converter_outputs_callout_contract_for_core_obsidian_types(tmp_path):
    html = _render_callout_fixture(tmp_path)
    parser = _TagCollector()
    parser.feed(html)

    assert parser.count_by_class("callout") == 4
    assert parser.count_by_class("callout-title") == 4
    assert parser.count_by_class("callout-icon") == 4
    assert parser.count_by_class("callout-body") == 4
    assert parser.count_by_attr("data-callout") == 4

    callout_classes = parser.classes_with_attr("data-callout")
    for expected in ["note", "warning", "question", "important"]:
        assert any(expected in class_names.split() for class_names in callout_classes)
        assert any(
            f"callout-{expected}" in class_names.split()
            for class_names in callout_classes
        )

    assert '<div class="callout-body">' in html
    assert "<strong>bold</strong>" in html
    assert "<code>code</code>" in html
    assert "<ul>" in html
    assert "<li>first item</li>" in html

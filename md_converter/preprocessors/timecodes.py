"""Preprocessor for static media timecode panels."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

from .base import Preprocessor


@dataclass(frozen=True)
class TimecodeEntry:
    """A parsed timecode line."""

    source: str
    seconds: int
    label: str


class TimecodesPreprocessor(Preprocessor):
    """Convert fenced ```timecodes blocks to accessible static HTML controls."""

    _fence_re = re.compile(
        r"(^|\n)```timecodes[ \t]*\n(?P<body>.*?)\n```(?=\n|$)",
        re.DOTALL,
    )
    _line_re = re.compile(
        r"^\s*(?P<time>(?:\d+:)?\d{1,2}:\d{2})(?:\s+|\s*-\s*)(?P<label>.*?)\s*$"
    )

    def process(self, content: str) -> str:
        """Replace timecode fences with raw HTML panels."""

        def replace(match: re.Match[str]) -> str:
            entries = self.parse_entries(match.group("body"))
            if not entries:
                return match.group(0)
            return f"{match.group(1)}{self.render_panel(entries)}"

        return self._fence_re.sub(replace, content)

    @classmethod
    def parse_entries(cls, body: str) -> list[TimecodeEntry]:
        """Parse supported MM:SS and H:MM:SS lines."""
        entries: list[TimecodeEntry] = []
        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            parsed = cls._line_re.match(line)
            if not parsed:
                continue
            source = parsed.group("time")
            label = parsed.group("label") or source
            entries.append(
                TimecodeEntry(source=source, seconds=cls._parse_timestamp(source), label=label)
            )
        return entries

    @staticmethod
    def _parse_timestamp(value: str) -> int:
        parts = [int(part) for part in value.split(":")]
        if len(parts) == 2:
            minutes, seconds = parts
            return minutes * 60 + seconds
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def render_panel(entries: list[TimecodeEntry]) -> str:
        buttons = []
        for entry in entries:
            safe_source = html.escape(entry.source, quote=True)
            safe_label = html.escape(entry.label, quote=True)
            buttons.append(
                "  <button type=\"button\" class=\"timecode-button\" "
                f"data-seek-seconds=\"{entry.seconds}\" aria-current=\"false\">"
                f"<span class=\"timecode-time\">{safe_source}</span> "
                f"<span class=\"timecode-label\">{safe_label}</span>"
                "</button>"
            )

        button_html = "\n".join(buttons)
        return (
            '<section class="timecode-panel" data-timecodes aria-label="Таймкоды">\n'
            '<div class="timecode-panel-title">Таймкоды</div>\n'
            f"{button_html}\n"
            "</section>"
        )

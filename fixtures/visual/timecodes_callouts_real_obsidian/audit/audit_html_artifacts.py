#!/usr/bin/env python3
"""Audit local src/href artifacts in rendered HTML files.

The report lists every src/href value. Data URLs and external URLs are reported
but not required to exist locally. Relative local references must exist relative
to the HTML file that contains them.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


TRACKED_ATTRS = {"src", "href"}
EXTERNAL_SCHEMES = {"http", "https", "mailto", "tel", "ftp", "javascript"}


@dataclass
class Reference:
    html_file: str
    tag: str
    attr: str
    value: str
    kind: str
    resolved_path: str | None
    exists: bool | None


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for attr, value in attrs:
            if attr in TRACKED_ATTRS and value:
                self.references.append((tag, attr, value))


def classify(value: str, html_file: Path) -> tuple[str, Path | None, bool | None]:
    stripped = value.strip()
    if not stripped:
        return "empty", None, None
    if stripped.startswith("data:"):
        return "data", None, None
    if stripped.startswith("#"):
        return "anchor", None, None

    parsed = urlparse(stripped)
    if parsed.scheme in EXTERNAL_SCHEMES or stripped.startswith("//"):
        return "external", None, None
    if parsed.scheme and parsed.scheme != "file":
        return "external", None, None

    if parsed.scheme == "file":
        candidate = Path(unquote(parsed.path))
    else:
        path_part = unquote(parsed.path)
        if not path_part:
            return "anchor", None, None
        candidate = Path(path_part)
        if not candidate.is_absolute():
            candidate = html_file.parent / candidate

    return "local", candidate, candidate.exists()


def audit_file(html_file: Path) -> list[Reference]:
    parser = LinkParser()
    parser.feed(html_file.read_text(encoding="utf-8"))
    refs: list[Reference] = []
    for tag, attr, value in parser.references:
        kind, resolved, exists = classify(value, html_file)
        reported_value = value
        if kind == "data":
            header = value.split(",", 1)[0]
            reported_value = f"{header},<data elided: {len(value)} chars>"
        refs.append(
            Reference(
                html_file=str(html_file),
                tag=tag,
                attr=attr,
                value=reported_value,
                kind=kind,
                resolved_path=str(resolved) if resolved else None,
                exists=exists,
            )
        )
    return refs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", nargs="+", help="HTML file(s) to audit")
    parser.add_argument("--json-out", help="Optional path for JSON report")
    args = parser.parse_args()

    all_refs: list[Reference] = []
    for raw in args.html:
        html_file = Path(raw)
        if not html_file.exists():
            print(f"HTML file not found: {html_file}", file=sys.stderr)
            return 2
        all_refs.extend(audit_file(html_file))

    missing = [ref for ref in all_refs if ref.kind == "local" and ref.exists is False]
    report = {
        "html_files": args.html,
        "counts": {
            "total": len(all_refs),
            "data": sum(1 for ref in all_refs if ref.kind == "data"),
            "external": sum(1 for ref in all_refs if ref.kind == "external"),
            "local": sum(1 for ref in all_refs if ref.kind == "local"),
            "local_missing": len(missing),
        },
        "references": [asdict(ref) for ref in all_refs],
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")

    if missing:
        print("Missing local artifact(s):", file=sys.stderr)
        for ref in missing:
            print(f"- {ref.html_file}: {ref.value} -> {ref.resolved_path}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

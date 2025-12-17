"""Препроцессор для Mermaid диаграмм."""

import re
from .base import Preprocessor


class MermaidPreprocessor(Preprocessor):
    """
    Преобразует Mermaid блоки для HTML:
    ```mermaid → <pre class="mermaid">
    Для EPUB оставляет как есть (обработает mermaid-filter).
    """

    def __init__(self, format_type: str = "html"):
        """
        Args:
            format_type: "html" или "epub"
        """
        self.format_type = format_type

    def process(self, content: str) -> str:
        """Обработка Mermaid блоков."""
        if self.format_type != "html":
            return content

        def replace_mermaid(match):
            diagram_code = match.group(1)
            return f'<pre class="mermaid">\n{diagram_code}\n</pre>'

        content = re.sub(
            r"```mermaid\n(.*?)\n```", replace_mermaid, content, flags=re.DOTALL
        )
        return content

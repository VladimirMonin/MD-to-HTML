"""Препроцессор для Diff блоков (из main.py)."""

import re
from .base import Preprocessor


class DiffPreprocessor(Preprocessor):
    """
    Обрабатывает diff блоки:
    ```diff-python
    - old code
    + new code
    ```
    Создает HTML структуру "Было/Стало".
    """

    def process(self, content: str) -> str:
        """Обработка diff блоков."""
        lines = content.split("\n")
        new_lines = []
        in_diff_block = False
        diff_block_lines: list[str] = []
        lang = ""

        for line in lines:
            if line.strip().startswith("```diff"):
                in_diff_block = True
                diff_block_lines = []
                # Извлекаем язык (например, ```diff-python)
                match = re.match(r"```diff-?(\w+)", line.strip())
                lang = match.group(1) if match else ""
                continue
            elif line.strip() == "```" and in_diff_block:
                in_diff_block = False

                # Разделяем на "было" и "стало"
                before_code = "\n".join(
                    [l[1:] for l in diff_block_lines if not l.startswith("+")]
                )
                after_code = "\n".join(
                    [l[1:] for l in diff_block_lines if not l.startswith("-")]
                )

                # Экранируем HTML
                before_code = self._escape(before_code)
                after_code = self._escape(after_code)

                # Генерируем HTML
                css_class = f"language-{lang}" if lang else ""
                html = f'''
<div class="diff-wrapper">
    <div class="diff-container">
        <div class="diff-column">
            <h4>Было:</h4>
            <pre><code class="{css_class}">{before_code}</code></pre>
        </div>
        <div class="diff-column">
            <h4>Стало:</h4>
            <pre><code class="{css_class}">{after_code}</code></pre>
        </div>
    </div>
</div>
'''
                new_lines.append(html)
            elif in_diff_block:
                diff_block_lines.append(line)
            else:
                new_lines.append(line)

        return "\n".join(new_lines)

    def _escape(self, text: str) -> str:
        """Экранирует HTML символы."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

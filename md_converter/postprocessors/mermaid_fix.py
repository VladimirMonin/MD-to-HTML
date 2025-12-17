"""Постпроцессор для исправления Mermaid символов."""

import re


class MermaidFixPostprocessor:
    """Исправляет экранированные символы в Mermaid блоках."""

    def process(self, html: str) -> str:
        """
        Восстанавливает символы которые Pandoc экранировал:
        --&gt; → -->
        """

        def fix_mermaid_block(match):
            block = match.group(1)
            block = block.replace("--&gt;", "-->")
            block = block.replace("&gt;", ">")
            block = block.replace("&lt;", "<")
            block = block.replace("&amp;", "&")
            return f'<pre class="mermaid">{block}</pre>'

        html = re.sub(
            r'<pre class="mermaid">(.*?)</pre>',
            fix_mermaid_block,
            html,
            flags=re.DOTALL,
        )

        print("✓ Mermaid символы исправлены")
        return html

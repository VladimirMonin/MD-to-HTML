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

            # Убираем <pre><code class="language-text"> которые Pandoc добавил
            block = re.sub(
                r"<pre[^>]*><code[^>]*>(.*?)</code></pre>",
                r"\1",
                block,
                flags=re.DOTALL,
            )

            # Конвертируем литеральные \n в настоящие переносы строк для multiline notes
            block = block.replace("\\n", "\n")

            # КРИТИЧЕСКИ ВАЖНО: HTML entities для переносов строк
            block = block.replace("&lt;br /&gt;", "\n")
            block = block.replace("&lt;br/&gt;", "\n")
            block = block.replace("&lt;br&gt;", "\n")

            # Pandoc entities для стрелок
            block = block.replace("--&gt;", "-->")
            block = block.replace("-&gt;", "->")
            block = block.replace("=&gt;", "=>")
            block = block.replace("&lt;|--", "<|--")
            block = block.replace("|&gt;", "|>")

            # Убираем лишние <p> теги если остались
            block = block.replace("<p>", "").replace("</p>", "")

            return f'<div class="mermaid">{block.strip()}</div>'

        html = re.sub(
            r'<div class="mermaid">(.*?)</div>',
            fix_mermaid_block,
            html,
            flags=re.DOTALL,
        )

        print("✓ Mermaid символы исправлены")
        return html

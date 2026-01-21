"""Постпроцессор для исправления Mermaid символов."""

import html
import re


class MermaidFixPostprocessor:
    """Исправляет экранированные символы в Mermaid блоках."""

    def process(self, html_content: str) -> str:
        """
        Восстанавливает символы которые Pandoc экранировал.
        Использует html.unescape() для универсального декодирования всех HTML entities.
        """

        def fix_mermaid_block(match):
            block = match.group(1)

            # Убираем <pre><code> обёртки которые Pandoc добавил
            # Вариант 1: <pre class="text"><code>...</code></pre>
            # Вариант 2: <pre><code class="language-text">...</code></pre>
            # Вариант 3: <pre class="text"><code>...</code> (без закрывающего </pre>)
            block = re.sub(
                r"<pre[^>]*>\s*<code[^>]*>(.*?)</code>(?:\s*</pre>)?",
                r"\1",
                block,
                flags=re.DOTALL,
            )

            # НЕ конвертируем литеральные \n - Mermaid note использует \n как символ переноса
            # block.replace("\\n", "\n") - удалено, так как ломает note for X "line1\nline2"

            # Убираем лишние <p> теги если остались
            block = block.replace("<p>", "").replace("</p>", "")

            # УНИВЕРСАЛЬНОЕ РЕШЕНИЕ: декодируем ВСЕ HTML entities
            # Это восстановит: &quot; → ", &amp; → &, &lt; → <, &gt; → >,
            # &apos; → ', числовые коды (&#39;, &#34; и т.д.)
            block = html.unescape(block)

            # После unescape заменяем временные маркеры на entity codes
            # (они были добавлены в препроцессоре для экранирования кавычек в note)
            block = block.replace("___APOS___", "&#39;")

            # Нормализуем варианты переноса строк в <br/> — Mermaid 11 ожидает слэш
            block = block.replace("<br />", "<br/>")
            block = block.replace("<br>", "<br/>")

            return f'<div class="mermaid">{block.strip()}</div>'

        # Ищем как <div>, так и <pre> — Pandoc может преобразовать div в pre
        html_content = re.sub(
            r'<(?:div|pre) class="mermaid">(.*?)</(?:div|pre)>',
            fix_mermaid_block,
            html_content,
            flags=re.DOTALL,
        )

        print("✓ Mermaid символы исправлены (html.unescape)")
        return html_content

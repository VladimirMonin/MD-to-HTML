"""Процессор для работы с HTML шаблонами."""

from pathlib import Path
from ..config import FeaturesConfig


class TemplateProcessor:
    """Генерирует HTML headers для Pandoc."""

    def __init__(self, template: str, features: FeaturesConfig):
        """
        Args:
            template: "book" или "web"
            features: Конфигурация функций
        """
        self.template = template
        self.features = features

    def build_header(self, format_type: str) -> str:
        """
        Генерирует HTML header для Pandoc --include-in-header.

        Args:
            format_type: "html" или "epub"

        Returns:
            HTML код для вставки в <head>
        """
        if format_type == "epub":
            return ""  # EPUB не нужен header

        # ИСПРАВЛЕНИЕ БАГ #3: Правильные пути к CSS модулям
        css_files = [
            "assets/css/modules/base.css",
            "assets/css/modules/components.css",
            "assets/css/modules/admonitions.css",
        ]

        if self.features.toc:
            css_files.append("assets/css/modules/toc.css")
        if self.features.breadcrumbs:
            css_files.append("assets/css/modules/breadcrumbs.css")
        if self.features.fullscreen or self.features.code_copy:
            css_files.append("assets/css/modules/interactive.css")
        if self.features.diff_blocks:
            css_files.append("assets/css/modules/diff.css")

        css_files.append("assets/css/modules/responsive.css")

        # Генерируем <link> теги
        css_html = "\n".join(
            [f'<link rel="stylesheet" href="{css}">' for css in css_files]
        )

        # Собираем JS
        js_code = self._get_js_code()

        # ИСПРАВЛЕНИЕ БАГ #2: HTML контейнер для breadcrumbs
        breadcrumbs_html = ""
        if self.features.breadcrumbs:
            breadcrumbs_html = (
                '<nav class="breadcrumbs-dynamic" aria-label="Навигация"></nav>'
            )

        # ИСПРАВЛЕНИЕ БАГ #13: highlight.js после загрузки DOM
        hljs_html = f"""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script>document.addEventListener('DOMContentLoaded', function() {{ hljs.highlightAll(); }});</script>
"""

        # Mermaid CDN
        mermaid_html = ""
        if self.features.mermaid:
            mermaid_html = """
<script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
</script>
"""

        return f"""
{breadcrumbs_html}
{css_html}
{hljs_html}
{mermaid_html}
<script>
{js_code}

// Инициализация всех модулей после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {{
    console.log('🚀 Initializing MD-to-HTML features...');
    
    // Инициализация функций (если они определены)
    if (typeof addCodeCopyButtons === 'function') addCodeCopyButtons();
    if (typeof enableFullscreenMedia === 'function') enableFullscreenMedia();
    if (typeof initDynamicBreadcrumbs === 'function') initDynamicBreadcrumbs();
    if (typeof smoothScrollTOC === 'function') smoothScrollTOC();
    
    console.log('✅ All features initialized');
}});
</script>
"""

    def _get_js_code(self) -> str:
        """Читает и объединяет JS файлы, удаляя export для inline."""
        js_modules = []

        if self.features.code_copy:
            js_modules.append("assets/js/modules/codeCopy.js")
        if self.features.fullscreen:
            js_modules.append("assets/js/modules/fullscreen.js")
        if self.features.breadcrumbs:
            js_modules.append("assets/js/modules/breadcrumbs.js")
        if self.features.toc:
            js_modules.append("assets/js/modules/smoothScroll.js")

        # Читаем все модули
        js_code = []
        for module_path in js_modules:
            path = Path(module_path)
            if path.exists():
                code = path.read_text(encoding="utf-8")
                # ИСПРАВЛЕНИЕ БАГ #1: Удаляем export для inline-скрипта
                code = code.replace("export function", "function")
                code = code.replace("export const", "const")
                code = code.replace("export default", "")
                js_code.append(code)

        return "\n\n".join(js_code)

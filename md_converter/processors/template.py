"""Процессор для работы с HTML шаблонами."""

import sys
from pathlib import Path
from ..config import FeaturesConfig, StylesConfig


class TemplateProcessor:
    """Генерирует HTML headers для Pandoc."""

    def __init__(
        self,
        template: str,
        features: FeaturesConfig,
        styles: StylesConfig,
        media_mode: str = "embed",
    ):
        """
        Args:
            template: "book" или "web"
            features: Конфигурация функций
            styles: Конфигурация стилей (темы)
            media_mode: "embed" (inline CSS) или "copy" (ссылки на CSS)
        """
        self.template = template
        self.features = features
        self.styles = styles
        self.media_mode = media_mode
        self.mermaid_panzoom_enabled = bool(features.mermaid_panzoom) and media_mode == "copy"

    def build_header(self, format_type: str, asset_base: str = "assets") -> str:
        """
        Генерирует HTML header для Pandoc --include-in-header.

        Args:
            format_type: "html" или "epub"
            asset_base: путь к папке assets относительно output HTML

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
        if self.mermaid_panzoom_enabled:
            css_files.append("assets/css/modules/mermaid-panzoom.css")
        if self.features.diff_blocks:
            css_files.append("assets/css/modules/diff.css")
        if self.features.plyr:
            css_files.append("assets/css/modules/media.css")
        if self.features.timecodes:
            css_files.append("assets/css/modules/timecodes.css")

        css_files.append("assets/css/modules/responsive.css")

        # Генерируем CSS (inline или ссылки)
        if self.media_mode == "embed":
            css_html = self._get_inline_css(css_files)
        else:
            # Режим copy - ссылки на файлы
            css_html = "\n".join(
                [
                    f'<link rel="stylesheet" href="{self._asset_href(css, asset_base)}">'
                    for css in css_files
                ]
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

        # Plyr - медиаплеер для audio/video
        plyr_html = ""
        if self.features.plyr:
            plyr_html = """
<link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css">
<script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
"""

        return f"""
{breadcrumbs_html}
{css_html}
{hljs_html}
{plyr_html}
<script>
{js_code}

// Инициализация всех модулей после загрузки DOM
document.addEventListener('DOMContentLoaded', function() {{
    console.log('🚀 Initializing MD-to-HTML features...');
    
    // Инициализация функций (если они определены)
    if (typeof addCodeCopyButtons === 'function') addCodeCopyButtons();
    if (typeof enableFullscreenMedia === 'function') enableFullscreenMedia();
    if (typeof initMermaidPanZoom === 'function') initMermaidPanZoom();
    if (typeof initDynamicBreadcrumbs === 'function') initDynamicBreadcrumbs();
    if (typeof smoothScrollTOC === 'function') smoothScrollTOC();
    
    // Инициализация Plyr медиаплеера
    if (typeof Plyr !== 'undefined') {{
        const players = Plyr.setup('.plyr-video, .plyr-audio, video, audio', {{
            controls: ['play-large', 'play', 'progress', 'current-time', 
                       'duration', 'mute', 'volume', 'settings', 'fullscreen'],
            settings: ['quality', 'speed'],
            speed: {{ selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] }}
        }});
        players.forEach(function(player) {{
            if (player && player.media) player.media.__mdToHtmlPlyr = player;
        }});
        console.log('🎬 Initialized ' + players.length + ' Plyr instances');
    }} else {{
        console.warn('⚠️ Plyr library not loaded');
    }}

    // Инициализация статических таймкодов после Plyr, но без жёсткой зависимости от него
    if (typeof initTimecodes === 'function') initTimecodes();
    
    console.log('✅ All features initialized');
}});
</script>
"""

    @staticmethod
    def _asset_href(asset_path: str, asset_base: str) -> str:
        """Переписать package-relative assets/... в output-relative href."""
        if asset_path == "assets":
            return asset_base
        if asset_path.startswith("assets/"):
            return f"{asset_base}/{asset_path[len('assets/') :]}"
        return asset_path

    def _get_inline_css(self, css_files: list[str]) -> str:
        """
        Читает CSS файлы и возвращает их как inline <style>.

        Args:
            css_files: Список путей к CSS файлам

        Returns:
            HTML с inline стилями
        """
        project_root = Path(__file__).parent.parent.parent
        css_content = []

        for css_file in css_files:
            path = project_root / css_file
            if path.exists():
                content = path.read_text(encoding="utf-8")
                css_content.append(f"/* {css_file} */\n{content}")
            else:
                print(f"⚠️ Не найден CSS файл: {path}", file=sys.stderr)

        if css_content:
            combined_css = "\n\n".join(css_content)
            return f'<style type="text/css">\n{combined_css}\n</style>'
        return ""

    def _get_js_code(self) -> str:
        """Читает и объединяет JS файлы, удаляя export для inline."""
        # Получаем корень проекта (где находится папка assets)
        project_root = Path(__file__).parent.parent.parent

        js_modules = []

        if self.features.code_copy:
            js_modules.append("assets/js/modules/codeCopy.js")
        if self.features.fullscreen:
            js_modules.append("assets/js/modules/fullscreen.js")
        if self.features.breadcrumbs:
            js_modules.append("assets/js/modules/breadcrumbs.js")
        if self.features.toc:
            js_modules.append("assets/js/modules/smoothScroll.js")
        if self.features.plyr:
            js_modules.append("assets/js/modules/media.js")
        if self.features.timecodes:
            js_modules.append("assets/js/modules/timecodes.js")
        if self.mermaid_panzoom_enabled:
            js_modules.append("assets/js/modules/mermaidPanZoom.js")

        # Читаем все модули
        js_code = []
        for module_path in js_modules:
            # Используем абсолютный путь от корня проекта
            path = project_root / module_path
            if path.exists():
                code = path.read_text(encoding="utf-8")
                # ИСПРАВЛЕНИЕ БАГ #1: Удаляем export для inline-скрипта
                code = code.replace("export function", "function")
                code = code.replace("export const", "const")
                code = code.replace("export default", "")
                js_code.append(code)
            else:
                print(f"⚠️ Не найден модуль: {path}", file=sys.stderr)

        return "\n\n".join(js_code)

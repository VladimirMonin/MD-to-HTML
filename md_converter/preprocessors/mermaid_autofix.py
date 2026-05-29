"""Постпроцессор для автоматического исправления типичных ошибок в Mermaid диаграммах."""

import re
from typing import Dict, List


class MermaidAutoFixPreprocessor:
    """
    Автоматически исправляет типичные ошибки AI-генераторов в Mermaid диаграммах:

    1. sequenceDiagram: <<text>> в сообщениях → «text» (Mermaid не поддерживает <<>> в labels)
    2. sequenceDiagram: валидация activate/deactivate стека
    3. classDiagram: типы возврата через пробел остаются (поддерживаются)
    """

    def __init__(self, format_type: str = "html"):
        self.format_type = format_type

    def _fix_sequence_diagram(self, diagram_code: str) -> str:
        """
        Исправляет типичные ошибки в sequenceDiagram.

        Проблема: AI пишет Service->>Ord: <<create>>
        Mermaid НЕ поддерживает <<>> в message labels (только для stereotypes)
        Решение: заменяем на французские кавычки «»
        """
        lines = diagram_code.split("\n")
        fixed_lines = []
        active_stack: List[str] = []  # Стек активных участников
        fixes = []

        for line in lines:
            original_line = line

            # 1. Исправляем <<text>> в сообщениях
            # Паттерн: A->>B: <<something>>
            # НЕ трогаем participant X <<stereotype>>
            if ("->>" in line or "-->" in line) and ":" in line:
                # Это сообщение: заменяем << >> только в label после двоеточия.
                # Нельзя делать replace по всей строке: иначе стрелка A->>B ломается в A-»B.
                prefix, label = line.split(":", 1)
                if "<<" in label:
                    label = label.replace("<<", "«").replace(">>", "»")
                    line = f"{prefix}:{label}"

            # 2. Валидация activate/deactivate
            # ВАЖНО: проверяем, что это отдельная директива, а не часть стрелки A->>Ord:
            activate_match = re.search(r"^\s*activate\s+(\w+)", line)
            if activate_match:
                participant = activate_match.group(1)
                active_stack.append(participant)

            deactivate_match = re.search(r"^\s*deactivate\s+(\w+)", line)
            if deactivate_match:
                participant = deactivate_match.group(1)
                # Проверяем, что деактивируем ПОСЛЕДНИЙ активированный
                if active_stack and active_stack[-1] != participant:
                    # ОШИБКА: деактивируем не того
                    correct_participant = active_stack[-1]
                    fixes.append(f"deactivate {participant} → {correct_participant}")
                    line = line.replace(
                        f"deactivate {participant}", f"deactivate {correct_participant}"
                    )
                    active_stack.pop()
                elif active_stack:
                    active_stack.pop()

            fixed_lines.append(line)

        if fixes:
            for fix in fixes:
                print(f"  ⚠️  Mermaid auto-fix: {fix}")

        return "\n".join(fixed_lines)

    def _fix_class_diagram(self, diagram_code: str) -> str:
        """
        Исправляет типичные ошибки в classDiagram.

        Проблема: AI пишет <<interface>>, <<abstract>> внутри class body
        Mermaid 11.12.2 НЕ поддерживает stereotypes внутри классов
        Решение: удаляем эти строки
        """
        lines = diagram_code.split("\n")
        fixed_lines = []
        removed_stereotypes = []

        for line in lines:
            # Удаляем строки с <<interface>>, <<abstract>> и другими стереотипами
            if re.search(r"^\s*<<\w+>>\s*$", line):
                match = re.search(r"<<(\w+)>>", line)
                if match:
                    stereotype = match.group(1)
                    if stereotype not in removed_stereotypes:
                        removed_stereotypes.append(stereotype)
                continue  # Пропускаем эту строку

            fixed_lines.append(line)

        if removed_stereotypes:
            print(
                f"  ⚠️  Mermaid auto-fix: удалены стереотипы {', '.join(f'<<{s}>>' for s in removed_stereotypes)} из classDiagram"
            )

        return "\n".join(fixed_lines)

    def process(self, content: str) -> str:
        """Обработка всех Mermaid блоков в документе."""

        fixes_applied = []

        def fix_mermaid_block(match):
            diagram_code = match.group(1)
            original_code = diagram_code
            diagram_type = (
                diagram_code.strip().split()[0] if diagram_code.strip() else ""
            )

            # Применяем автоисправления в зависимости от типа диаграммы
            if diagram_type == "sequenceDiagram":
                diagram_code = self._fix_sequence_diagram(diagram_code)
                if "<<" in original_code or ">>" in original_code:
                    if "<<" in original_code and "->>" in original_code:
                        fixes_applied.append("sequenceDiagram: << >> → « »")
            elif diagram_type == "classDiagram":
                diagram_code = self._fix_class_diagram(diagram_code)

            # Возвращаем обратно
            return f"```mermaid\n{diagram_code}\n```"

        # Обрабатываем все ```mermaid блоки
        content = re.sub(
            r"```mermaid\n(.*?)\n```", fix_mermaid_block, content, flags=re.DOTALL
        )

        if fixes_applied:
            print(f"  🔧 Mermaid auto-fix: {', '.join(fixes_applied)}")

        return content

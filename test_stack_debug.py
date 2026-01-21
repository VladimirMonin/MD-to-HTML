"""Отладка автоисправления."""

import re

diagram = """sequenceDiagram
    activate Repo
    Repo-->>Service: result_id
    deactivate Ord"""

lines = diagram.split("\n")
active_stack = []

for i, line in enumerate(lines):
    print(f"Line {i}: {repr(line)}")

    activate_match = re.search(r"activate\s+(\w+)", line)
    if activate_match:
        participant = activate_match.group(1)
        print(f"  → ACTIVATE: {participant}")
        active_stack.append(participant)
        print(f"  → Stack: {active_stack}")

    deactivate_match = re.search(r"deactivate\s+(\w+)", line)
    if deactivate_match:
        participant = deactivate_match.group(1)
        print(f"  → DEACTIVATE: {participant}")
        if active_stack:
            print(f"  → Expected: {active_stack[-1]}")
            if active_stack[-1] != participant:
                print(
                    f"  → ERROR! Should deactivate {active_stack[-1]}, not {participant}"
                )
        else:
            print(f"  → Stack empty!")

"""Быстрый тест автоисправления."""

import sys

sys.path.insert(0, "c:/PY/MD_to_HTML")

from md_converter.preprocessors.mermaid_autofix import MermaidAutoFixPreprocessor

test_md = """# Test

```mermaid
sequenceDiagram
    activate Repo
    Repo-->>Service: result_id
    deactivate Ord
```
"""

print("ИСХОДНИК:")
print(test_md)

fixer = MermaidAutoFixPreprocessor()
result = fixer.process(test_md)

print("\nРЕЗУЛЬТАТ:")
print(result)

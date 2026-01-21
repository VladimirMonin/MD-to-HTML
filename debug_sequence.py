"""Debug script для проверки обработки sequenceDiagram с <<create>>."""

from md_converter.preprocessors import MermaidPreprocessor
from md_converter.postprocessors import MermaidFixPostprocessor

test_md = """# Test: SequenceDiagram с <<create>>

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as OrderService
    participant Ord as Order
    participant Val as Validator
    participant Repo as Repository

    User->>Service: create(data)
    activate Service
    
    Note right of Service: 1. Создание объекта
    Service->>Ord: <<create>>
    activate Ord
    Ord-->>Service: order_instance
    deactivate Ord

    Note right of Service: 2. Проверка логики
    Service->>Val: validate(order_instance)
    activate Val
    Val-->>Service: is_valid (True)
    deactivate Val

    Note right of Service: 3. Сохранение
    Service->>Repo: save(order_instance)
    activate Repo
    Repo-->>Service: result_id
    deactivate Repo

    Service-->>User: Order Created (201 Created)
    deactivate Service
```
"""

print("=" * 70)
print("ИСХОДНИК:")
print("=" * 70)
print(test_md)

print("\n" + "=" * 70)
print("ПОСЛЕ ПРЕПРОЦЕССОРА:")
print("=" * 70)
preprocessor = MermaidPreprocessor(format_type="html")
after_preproc = preprocessor.process(test_md)
print(after_preproc)

# Проверяем наличие <<create>>
if "<<create>>" in after_preproc:
    print("\n✅ <<create>> СОХРАНЕН после препроцессора")
else:
    print("\n❌ <<create>> ПОТЕРЯН после препроцессора")

# Симулируем что Pandoc может сделать (обычно он экранирует < и >)
print("\n" + "=" * 70)
print("СИМУЛЯЦИЯ PANDOC (экранирование < и >):")
print("=" * 70)
# Pandoc обычно НЕ трогает содержимое raw HTML блоков {=html}
# Но на всякий случай проверим
simulated_pandoc = after_preproc.replace("<<create>>", "&lt;&lt;create&gt;&gt;")
print(simulated_pandoc)

print("\n" + "=" * 70)
print("ПОСЛЕ ПОСТПРОЦЕССОРА:")
print("=" * 70)
postprocessor = MermaidFixPostprocessor()
after_postproc = postprocessor.process(simulated_pandoc)
print(after_postproc)

# Финальная проверка
if "<<create>>" in after_postproc:
    print("\n✅ <<create>> ВОССТАНОВЛЕН после постпроцессора")
else:
    print("\n❌ <<create>> НЕ ВОССТАНОВЛЕН после постпроцессора")

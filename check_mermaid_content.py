import re

with open("test_output/mermaid_tests/sequence_create.html", "r", encoding="utf-8") as f:
    html = f.read()

# Находим mermaid блок
match = re.search(r'<div class="mermaid">(.*?)</div>', html, re.DOTALL)
if match:
    mermaid_content = match.group(1)
    print("=== СОДЕРЖИМОЕ MERMAID БЛОКА ===")
    print(repr(mermaid_content[:500]))
    print("\n=== ПОИСК <<create>> ===")
    if "<<create>>" in mermaid_content:
        print("✅ <<create>> НАЙДЕН")
        # Находим строку с <<create>>
        for line in mermaid_content.split("\n"):
            if "create" in line.lower():
                print(f"   {repr(line)}")
    else:
        print("❌ <<create>> НЕ НАЙДЕН")
        print("\nВозможные варианты:")
        for variant in ["&lt;&lt;create&gt;&gt;", "<\<create>>"]:
            if variant in mermaid_content:
                print(f"   Найдено: {variant}")
else:
    print("❌ Mermaid блок не найден в HTML")

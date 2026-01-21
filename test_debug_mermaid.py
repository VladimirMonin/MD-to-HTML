"""Debug mermaid preprocessing."""

from md_converter.preprocessors.mermaid_preprocessor import MermaidPreprocessor

diagram_md = """# Test: ClassDiagram

```mermaid
classDiagram
    class BaseAI {
        <<abstract>>
        +config: Config
        #_client: Mistral
        +generate(prompt)*
        #_send_request(messages)
    }
    
    class TextGenerator {
        +system_prompt: str
        +previous_context: str
        +generate(prompt)
        -_build_messages(prompt)
        -_load_prompt()
    }
    
    BaseAI <|-- TextGenerator : наследует
    
    note for BaseAI "Отвечает за 'КАК отправить'\\n(транспортный слой)"
    note for TextGenerator "Отвечает за 'ЧТО отправить'\\n(слой логики)"
```
"""

print("=== INPUT ===")
for line in diagram_md.split("\n"):
    if "note" in line.lower():
        print(repr(line))

prep = MermaidPreprocessor(format_type="html")
result = prep.process(diagram_md)

print("\n=== RESULT ===")
for line in result.split("\n"):
    if "note" in line.lower():
        print(repr(line))

print("\n=== FULL RESULT ===")
print(result)

# Тест исправления Mermaid

Проверяем, что диаграмма с `<br/>`, кавычками и эмодзи корректно рендерится:

```mermaid
flowchart TD
    %% Определение стилей
    classDef action fill:#4ecdc4,stroke:#0a9396,color:#fff
    classDef decision fill:#ffd93d,stroke:#f4a261,color:#000
    classDef error fill:#ff6b6b,stroke:#c92a2a,color:#fff
    classDef noteStyle fill:#fff5ad,stroke:#d4c46a,color:#333

    Start[Попытка записи: obj.value = x]:::action --> CallSetter[@value.setter]:::action
    CallSetter --> Validate{Валидация<br/>пройдена?}:::decision
    
    Validate -- "Да ✅" --> Save[self._value = x]:::action
    Validate -- "Нет ❌" --> RaiseErr[raise ValueError]:::error
    
    Save --> End((Готово)):::action
    RaiseErr --> End
    
    Note["📝 Сеттер работает как фильтр,<br/>не пропуская мусор внутрь объекта"]:::noteStyle
    CallSetter -.- Note
```

## Проверяемые символы

- `<br/>` в узлах
- Кавычки `"` в метках
- Эмодзи: 📝, ✅, ❌
- Комментарии `%%`
- Классы и стили

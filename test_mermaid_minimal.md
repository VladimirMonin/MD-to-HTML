# Тест 1: Минимальная диаграмма

```mermaid
flowchart TD
    A[Start] --> B[End]
```

# Тест 2: С кириллицей

```mermaid
flowchart TD
    A[Начало] --> B[Конец]
```

# Тест 3: С Unicode эмодзи (в кавычках)

```mermaid
flowchart TD
    A["Да ✅"] --> B["Нет ❌"]
```

# Тест 4: С br тегом

```mermaid
flowchart TD
    A{Валидация<br/>пройдена?} --> B[Да]
```

# Тест 5: С @ символом (проблемный!)

```mermaid
flowchart TD
    A[Start] --> B["@value.setter"]
```

# Тест 6: Edge labels с Unicode

```mermaid
flowchart TD
    A --> |"Да ✅"| B
```

# Тест 7: classDef

```mermaid
flowchart TD
    classDef action fill:#4ecdc4
    A[Test]:::action
```

# Тест 8: Комплексный (без @)

```mermaid
flowchart TD
    classDef action fill:#4ecdc4,stroke:#0a9396,color:#fff
    Start["Начало работы"] --> Validate{Валидация<br/>пройдена?}
    Validate -->|"Да"| Save[Сохранить]
    Validate -->|"Нет"| Error[Ошибка]
```

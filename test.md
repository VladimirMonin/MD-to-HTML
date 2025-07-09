# Тестовый документ для проверки Mermaid

Это тестовый документ, чтобы убедиться, что диаграммы Mermaid и другая Markdown-разметка отображаются правильно.

## Простая диаграмма последовательности

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>John: Hello John, how are you?
    loop Healthcheck
        John->>John: Fight against hypochondria
    end
    Note right of John: Rational thoughts<br/>prevail...
    John-->>Alice: Great!
    John->>Bob: How about you?
    Bob-->>John: Jolly good!
```

## Диаграмма Ганта

```mermaid
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
    A task           :a1, 2024-01-01, 30d
    Another task     :after a1  , 20d
    section Another
    Task in sec      :2024-01-12  , 12d
    another task      : 24d
```

## Блок с кодом на Python

```python
def hello_world():
    print("Hello, world!")

hello_world()
```

## Список

- Элемент 1
- Элемент 2
  - Вложенный элемент 2.1
  - Вложенный элемент 2.2
- Элемент 3

> [!info]
> Это информационный блок для проверки стилей.

Все готово для теста!
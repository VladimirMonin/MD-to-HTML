# Комплексные Mermaid диаграммы

## Диаграмма 1: Unit и Integration тесты

```mermaid
graph TB
    subgraph Unit ["🔬 Уровень Unit (Изоляция)"]
        direction TB
        UTest["Тест"] -.-> UClass["Класс A"]
        note1["📝 Зависимости<br/>отрезаны фейками"]
    end

    subgraph Integration ["🏭 Уровень Integration (Связки)"]
        direction TB
        ITest["Тест"] --> IClassA["Класс A"]
        IClassA --> IClassB["Класс B"]
        IClassB --> FS[("📂 Файловая<br/>система")]
        note2["🎯 Проверяем стыковку<br/>и поток данных"]
    end
```

## Диаграмма 2: Компоненты системы

```mermaid
flowchart TD
    Main[("🚀 main.py<br/>(Точка входа)")]
    ConfigObj[("⚙️ Config Object<br/>(Экземпляр)")]
    
    subgraph Components ["Компоненты системы"]
        FP["📂 FileProcessor"]
        TG["✍️ TextGenerator"]
        IA["🖼️ ImageAnalyzer"]
        CC["⚙️ CourseCreator"]
    end

    Main -->|1. Загружает| ConfigObj
    ConfigObj -->|2. Передаётся в| FP
    ConfigObj -->|2. Передаётся в| TG
    ConfigObj -->|2. Передаётся в| IA
    ConfigObj -->|2. Передаётся в| CC

    style Main fill:#f9f,stroke:#333,stroke-width:2px,color:#000
    style ConfigObj fill:#ffd93d,stroke:#f4a261,stroke-width:2px,color:#000
    style Components fill:#e1f5fe,stroke:#01579b,stroke-dasharray: 5 5
```

## Диаграмма 3: ClassDiagram

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
    
    note for BaseAI "Отвечает за 'КАК отправить'\n(транспортный слой)"
    note for TextGenerator "Отвечает за 'ЧТО отправить'\n(слой логики)"
```

## Диаграмма 4: Pipeline обработки

```mermaid
flowchart LR
    Input[("📄 Input File\n(lesson.md)")]
    Splitter{"🔪 Splitter\n(Разбиение)"}
    Parser["🔍 Image Parser\n(Поиск картинок)"]
    Output[("📦 Output\nlist[ContentChunk]")]

    Input -->|"Сырой текст"| Splitter
    Splitter -->|"Разделитель ******"| Parser
    Parser -->|"Текст + Пути к фото"| Output

    style Input fill:#ff6b6b,stroke:#c92a2a,color:#fff
    style Splitter fill:#ffd93d,stroke:#f4a261,color:#000
    style Parser fill:#4ecdc4,stroke:#0a9396,color:#fff
    style Output fill:#e1f5fe,stroke:#01579b,color:#333
```

## Диаграмма 5: Память и накопление

```mermaid
graph TD
    subgraph Step1 [Шаг 1: Чистый лист]
        C1[Чанк 1] -->|Вход| G1(Генерация)
        G1 --> R1["Результат: 'Классы...'"]
    end

    subgraph Step2 [Шаг 2: Накопление]
        R1 -.->|Сохраняем| MEM2[("Память: 'Классы...'")]
        MEM2 -->|Контекст| G2(Генерация Чанка 2)
        G2 --> R2["Результат: 'Методы...'"]
    end

    subgraph Step3 [Шаг 3: Насыщение]
        R2 -.->|Добавляем| MEM3[("Память: 'Классы... Методы...'")]
        MEM3 -->|Контекст| G3(Генерация Чанка 3)
        G3 --> R3["Результат: 'Наследование...'"]
    end

    subgraph Step4 [Шаг 4: Обрезка ✂️]
        R3 -.->|Места нет! Удаляем старое| MEM4[("Память: '...ды... Методы... Наследование...'")]
        style MEM4 fill:#ff6b6b,stroke:#c92a2a,color:#fff
        
        note["❌ 'Класс...' удалено<br>✅ '...ды...' осталось"]
        MEM4 -.- note
        
        MEM4 -->|Урезанный контекст| G4(Генерация Чанка 4)
    end

    style Step1 fill:#f9f9f9,stroke:#333,stroke-width:1px
    style Step4 fill:#fff5f5,stroke:#ffcccc,stroke-width:2px
```

## Диаграмма 6: Полный Pipeline

```mermaid
flowchart TD
    classDef entry fill:#4ecdc4,stroke:#0a9396,color:#fff
    classDef config fill:#ffd93d,stroke:#f4a261,color:#000
    classDef logic fill:#e1f5fe,stroke:#01579b,color:#333
    classDef output fill:#ff6b6b,stroke:#c92a2a,color:#fff

    Start(("🚀 Запуск<br/>(main.py)")):::entry
    Config["⚙️ Загрузка Config<br/>(config.py)"]:::config
    Orchestrator["🤖 Инициализация CourseCreator<br/>(pipeline.py)"]:::logic
    
    subgraph Pipeline ["Внутри run_pipeline()"]
        direction TB
        Step1["📄 Чтение файла<br/>(FileProcessor)"]:::logic
        Step2["🖼️ Анализ изображений<br/>(ImageAnalyzer)"]:::logic
        Step3["✍️ Генерация текста<br/>(TextGenerator)"]:::logic
    end

    Result[("💾 Готовый файл<br/>(output/result.md)")]:::output

    Start --> Config
    Config --> Orchestrator
    Orchestrator --> Step1
    Step1 --> Step2
    Step2 --> Step3
    Step3 --> Result

    Note["Файл main.py связывает<br/>конфигурацию и оркестратор"]
    Start -.- Note
    style Note fill:#fff5ad,stroke:#d4c46a,color:#333
```

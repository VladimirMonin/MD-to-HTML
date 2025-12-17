# 📊 Коллекция диаграмм Mermaid

Демонстрация различных типов диаграмм для тестирования.

## 🔄 Flowchart диаграммы

### Простой процесс принятия решений

```mermaid
flowchart TD
    Start([Начало]) --> Input[Ввод данных]
    Input --> Check{Данные корректны?}
    Check -->|Да| Process[Обработка]
    Check -->|Нет| Error[Ошибка ввода]
    Process --> Save[(Сохранение)]
    Save --> End([Конец])
    Error --> Input
    
    classDef startEnd fill:#1f2937,stroke:#60a5fa,stroke-width:2px,color:#e5e7eb
    classDef process fill:#374151,stroke:#34d399,stroke-width:2px,color:#e5e7eb
    classDef decision fill:#4c1d95,stroke:#a78bfa,stroke-width:2px,color:#e5e7eb
    classDef storage fill:#831843,stroke:#f472b6,stroke-width:2px,color:#e5e7eb
    
    class Start,End startEnd
    class Input,Process,Error process
    class Check decision
    class Save storage
```

### Сложный бизнес-процесс

```mermaid
flowchart LR
    A[Заявка] --> B{Проверка документов}
    B -->|OK| C[Предварительное одобрение]
    B -->|Ошибка| D[Запрос дополнительных документов]
    D --> A
    C --> E[Оценка рисков]
    E --> F{Риски приемлемы?}
    F -->|Да| G[Одобрение]
    F -->|Нет| H[Отказ]
    G --> I[Выдача кредита]
    H --> J[Уведомление об отказе]
    
    classDef startNode fill:#065f46,stroke:#10b981,stroke-width:2px,color:#ffffff
    classDef processNode fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#ffffff
    classDef decisionNode fill:#7c2d12,stroke:#f97316,stroke-width:2px,color:#ffffff
    classDef endNode fill:#4c1d95,stroke:#8b5cf6,stroke-width:2px,color:#ffffff
    
    class A startNode
    class C,D,E,I,J processNode
    class B,F decisionNode
    class G,H endNode
```

## 📈 Sequence диаграммы

### Процесс авторизации

```mermaid
sequenceDiagram
    participant C as Client
    participant F as Frontend
    participant A as Auth API
    participant D as Database

    C->>F: Логин + пароль
    F->>A: POST /auth/login
    A->>D: Проверить пользователя
    D-->>A: Данные пользователя
    A->>A: Генерация JWT
    A-->>F: Token + User Info
    F-->>C: Перенаправление в приложение
```

### Микросервисная архитектура

```mermaid
sequenceDiagram
    participant U as User
    participant G as API Gateway
    participant A as Auth Service
    participant O as Order Service
    participant P as Payment Service
    participant N as Notification Service

    U->>G: Создать заказ
    G->>A: Проверить токен
    A-->>G: Токен валиден
    G->>O: Создать заказ
    O->>P: Обработать платеж
    P-->>O: Платеж успешен
    O->>N: Отправить уведомление
    N-->>U: Email подтверждение
    O-->>G: Заказ создан
    G-->>U: Успешный ответ
```

## 🗃️ ER диаграммы

### Система управления контентом

```mermaid
erDiagram
    USER ||--o{ POST : creates
    USER ||--o{ COMMENT : writes
    POST ||--o{ COMMENT : has
    CATEGORY ||--o{ POST : categorizes
    
    USER {
        int id PK
        string username UK
        string email UK
        string password_hash
        datetime created_at
        boolean is_active
        string role
    }

    POST {
        int id PK
        int author_id FK
        string title
        text content
        string status
        datetime created_at
        datetime updated_at
    }

    COMMENT {
        int id PK
        int post_id FK
        int author_id FK
        text content
        datetime created_at
        boolean is_approved
    }

    CATEGORY {
        int id PK
        string name
        string slug UK
        text description
    }
```

## 📊 Диаграммы состояний

### Жизненный цикл заказа

```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> Confirmed : Подтверждение
    Created --> Cancelled : Отмена
    
    Confirmed --> Processing : Начать обработку
    Processing --> Shipped : Отправить
    Processing --> Cancelled : Отменить
    
    Shipped --> Delivered : Доставить
    Shipped --> Returned : Возврат
    
    Delivered --> Completed : Закрыть
    Delivered --> Returned : Возврат
    
    Returned --> Refunded : Возврат средств
    Cancelled --> [*]
    Completed --> [*]
    Refunded --> [*]
```

### Состояния пользователя

```mermaid
stateDiagram-v2
    [*] --> Guest
    Guest --> Registered : Регистрация
    Registered --> EmailVerified : Подтверждение email
    EmailVerified --> Active : Активация
    
    Active --> Suspended : Нарушение
    Suspended --> Active : Разблокировка
    Suspended --> Banned : Серьезное нарушение
    
    Active --> Inactive : Длительное отсутствие
    Inactive --> Active : Возврат
    
    state Active {
        [*] --> Online
        Online --> Offline : Выход
        Offline --> Online : Вход
    }
    
    Banned --> [*]
```

## 📅 Gantt диаграммы

### План разработки продукта

```mermaid
gantt
    title Разработка мобильного приложения
    dateFormat YYYY-MM-DD
    axisFormat %d.%m

    section Планирование
    Исследование рынка        :done, research, 2024-01-01, 2024-01-15
    Анализ требований         :done, analysis, 2024-01-10, 2024-01-25
    Техническое планирование  :done, tech-plan, 2024-01-20, 2024-02-05

    section Дизайн
    UX исследование          :done, ux, 2024-01-25, 2024-02-10
    UI дизайн               :active, ui, 2024-02-05, 2024-02-25
    Прототипирование        :proto, 2024-02-15, 2024-03-05

    section Разработка
    Backend API             :backend, 2024-02-20, 2024-04-15
    iOS приложение          :ios, 2024-03-01, 2024-04-30
    Android приложение      :android, 2024-03-01, 2024-04-30
    Интеграционные тесты    :integration, 2024-04-15, 2024-05-05

    section Тестирование
    Альфа тестирование      :alpha, 2024-04-20, 2024-05-10
    Бета тестирование       :beta, 2024-05-05, 2024-05-25
    Финальное тестирование  :final, 2024-05-20, 2024-06-05

    section Запуск
    Подготовка к релизу     :release-prep, 2024-05-25, 2024-06-10
    Релиз в App Store       :app-store, 2024-06-05, 2024-06-15
    Релиз в Google Play     :google-play, 2024-06-05, 2024-06-15
```

## 🚀 Git диаграммы

### Gitflow модель

```mermaid
gitgraph
    commit id: "Initial"
    branch develop
    checkout develop
    commit id: "Setup"
    
    branch feature
    checkout feature
    commit id: "Feature A"
    commit id: "Feature B"
    
    checkout develop
    merge feature
    commit id: "Merge feature"
    
    checkout main
    merge develop
    commit id: "Release v1.0"
    
    branch hotfix
    checkout hotfix
    commit id: "Hotfix"
    
    checkout main
    merge hotfix
    commit id: "v1.0.1"
```

## 🏗️ Архитектурные диаграммы

### Микросервисная архитектура

```mermaid
graph TB
    subgraph "Client Layer"
        Web[Web App]
        Mobile[Mobile App]
    end

    subgraph "API Gateway"
        Gateway[API Gateway<br/>Rate Limiting, Auth]
    end

    subgraph "Services"
        Auth[Auth Service]
        User[User Service]
        Order[Order Service]
        Payment[Payment Service]
        Notification[Notification Service]
    end

    subgraph "Data Layer"
        UserDB[(User DB)]
        OrderDB[(Order DB)]
        PaymentDB[(Payment DB)]
        Cache[(Redis Cache)]
    end

    subgraph "External"
        PaymentGW[Payment Gateway]
        EmailSvc[Email Service]
    end

    Web --> Gateway
    Mobile --> Gateway
    Gateway --> Auth
    Gateway --> User
    Gateway --> Order
    Gateway --> Payment
    Gateway --> Notification

    Auth --> UserDB
    User --> UserDB
    Order --> OrderDB
    Payment --> PaymentDB
    
    User --> Cache
    Order --> Cache
    
    Payment --> PaymentGW
    Notification --> EmailSvc
```

## 🔄 User Journey диаграмма

### Процесс покупки

```mermaid
journey
    title Путь пользователя при покупке товара
    section Поиск товара
      Заходит на сайт         : 5: Customer
      Ищет товар             : 3: Customer
      Просматривает категории : 4: Customer
      Читает отзывы          : 4: Customer
    section Выбор товара
      Сравнивает товары      : 3: Customer
      Добавляет в корзину    : 5: Customer
      Проверяет корзину      : 4: Customer
    section Оформление заказа
      Заполняет данные       : 2: Customer
      Выбирает доставку      : 3: Customer
      Выбирает оплату        : 3: Customer
      Подтверждает заказ     : 4: Customer
    section После покупки
      Получает подтверждение : 5: Customer
      Отслеживает доставку   : 4: Customer
      Получает товар         : 5: Customer
      Оставляет отзыв        : 3: Customer
```

## 📊 Mindmap диаграмма

### Структура веб-приложения

```mermaid
mindmap
  root((Веб-приложение))
    Frontend
      React
        Components
        Hooks
        State Management
      Vue.js
        Composition API
        Vuex
      Angular
        Services
        Modules
    Backend
      Node.js
        Express
        Fastify
      Python
        Django
        FastAPI
      Java
        Spring Boot
    Database
      SQL
        PostgreSQL
        MySQL
      NoSQL
        MongoDB
        Redis
    DevOps
      Docker
      Kubernetes
      CI/CD
        GitHub Actions
        GitLab CI
```

---

## ✅ Заключение

Эта коллекция демонстрирует все основные типы диаграмм Mermaid:

- **Flowchart** - блок-схемы и процессы
- **Sequence** - диаграммы последовательности
- **ER** - диаграммы сущность-связь
- **State** - диаграммы состояний  
- **Gantt** - временные диаграммы
- **Git** - схемы ветвления
- **Architecture** - архитектурные схемы
- **Journey** - пользовательские сценарии
- **Mindmap** - интеллект-карты

> [!tip]
> Используйте эти примеры как основу для создания собственных диаграмм!

## 📚 Class диаграмма

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string password_hash
        +datetime created_at
        +boolean is_active
        +login()
        +logout()
    }

    class Post {
        +int id
        +int author_id
        +string title
        +text content
        +string status
        +datetime created_at
        +datetime updated_at
        +publish()
        +archive()
    }

    class Comment {
        +int id
        +int post_id
        +int author_id
        +text content
        +datetime created_at
        +boolean is_approved
        +approve()
        +reject()
    }

    class Category {
        +int id
        +string name
        +string slug
        +text description
    }

    class Tag {
        +int id
        +string name
    }

    class Media {
        +int id
        +string url
        +string type
        +int size
    }

    %% Отношения
    User "1" --> "*" Post : authors
    User "1" --> "*" Comment : writes
    Post "1" --> "*" Comment : has
    Post "1" --> "1" Category : belongsTo
    Post "*" --> "*" Tag : taggedWith
    Post "1" --> "*" Media : attachments
    Media o-- Post : optionalFor
```

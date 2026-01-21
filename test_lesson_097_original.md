# Урок 097 - ОРИГИНАЛ от AI-писателя

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
    deactivate Ord

    Service-->>User: Order Created (201 Created)
    deactivate Service
```

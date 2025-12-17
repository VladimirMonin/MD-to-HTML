# 💻 Демонстрация блоков кода и Diff

Примеры различных языков программирования и сравнений кода.

## 🐍 Python примеры

### Базовый класс

```python
from typing import List, Optional
from datetime import datetime
import logging

class TaskManager:
    """Менеджер задач с поддержкой приоритетов и дедлайнов."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.logger = logging.getLogger(__name__)
    
    def add_task(self, title: str, priority: int = 1, 
                 deadline: Optional[datetime] = None) -> Task:
        """Добавляет новую задачу в список."""
        task = Task(
            id=len(self.tasks) + 1,
            title=title,
            priority=priority,
            deadline=deadline,
            created_at=datetime.now()
        )
        self.tasks.append(task)
        self.logger.info(f"Добавлена задача: {task.title}")
        return task
    
    def get_urgent_tasks(self) -> List[Task]:
        """Возвращает список срочных задач."""
        now = datetime.now()
        return [
            task for task in self.tasks 
            if task.deadline and task.deadline <= now 
            and not task.is_completed
        ]
```

### Асинхронный код

```python
import asyncio
import aiohttp
from typing import AsyncGenerator

async def fetch_multiple_urls(urls: List[str]) -> AsyncGenerator[dict, None]:
    """Асинхронно загружает данные с нескольких URL."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                yield result
            except Exception as e:
                yield {"error": str(e), "url": None}

async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict:
    """Загружает данные с одного URL."""
    try:
        async with session.get(url, timeout=10) as response:
            data = await response.json()
            return {"url": url, "data": data, "status": response.status}
    except asyncio.TimeoutError:
        raise Exception(f"Timeout для {url}")
    except Exception as e:
        raise Exception(f"Ошибка загрузки {url}: {str(e)}")
```

## 🟨 JavaScript примеры

### Современный ES6+ код

```javascript
// Класс с приватными полями и методами
class DataAnalyzer {
    #data = [];
    #processed = false;
    
    constructor(initialData = []) {
        this.#data = [...initialData];
    }
    
    // Публичные методы
    async loadData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const newData = await response.json();
            this.#data.push(...newData);
            this.#processed = false;
            
            return this.#data.length;
        } catch (error) {
            console.error('Ошибка загрузки данных:', error);
            throw error;
        }
    }
    
    // Геттеры и сеттеры
    get dataCount() {
        return this.#data.length;
    }
    
    get isProcessed() {
        return this.#processed;
    }
    
    // Приватный метод
    #validateData() {
        return this.#data.every(item => 
            item && typeof item === 'object' && 'value' in item
        );
    }
    
    // Методы обработки данных
    process() {
        if (!this.#validateData()) {
            throw new Error('Некорректные данные');
        }
        
        this.#data = this.#data
            .filter(item => item.value != null)
            .map(item => ({
                ...item,
                processed: true,
                timestamp: Date.now()
            }))
            .sort((a, b) => b.value - a.value);
        
        this.#processed = true;
        return this;
    }
    
    // Генератор для итерации
    * getProcessedData() {
        if (!this.#processed) {
            throw new Error('Данные не обработаны');
        }
        
        for (const item of this.#data) {
            yield item;
        }
    }
}

// Использование с async/await и деструктуризацией
const analyzer = new DataAnalyzer();

const processDataPipeline = async (urls) => {
    const results = await Promise.allSettled(
        urls.map(url => analyzer.loadData(url))
    );
    
    const failed = results
        .filter(result => result.status === 'rejected')
        .map(result => result.reason);
    
    if (failed.length > 0) {
        console.warn('Некоторые URL не удалось загрузить:', failed);
    }
    
    return analyzer.process();
};
```

### React компонент

```javascript
import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { debounce } from 'lodash';

const UserList = ({ users, onUserSelect, searchDelay = 300 }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [sortBy, setSortBy] = useState('name');
    const [sortOrder, setSortOrder] = useState('asc');
    
    // Дебаунсированный поиск
    const debouncedSearch = useCallback(
        debounce((term) => {
            setSearchTerm(term);
        }, searchDelay),
        [searchDelay]
    );
    
    // Мемоизированная фильтрация и сортировка
    const filteredAndSortedUsers = useMemo(() => {
        let filtered = users;
        
        if (searchTerm) {
            filtered = users.filter(user =>
                user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                user.email.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }
        
        return filtered.sort((a, b) => {
            const aValue = a[sortBy];
            const bValue = b[sortBy];
            
            if (sortOrder === 'asc') {
                return aValue > bValue ? 1 : -1;
            } else {
                return aValue < bValue ? 1 : -1;
            }
        });
    }, [users, searchTerm, sortBy, sortOrder]);
    
    const handleSortChange = (field) => {
        if (sortBy === field) {
            setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortBy(field);
            setSortOrder('asc');
        }
    };
    
    return (
        <div className="user-list">
            <div className="search-controls">
                <input
                    type="text"
                    placeholder="Поиск пользователей..."
                    onChange={(e) => debouncedSearch(e.target.value)}
                    className="search-input"
                />
                
                <div className="sort-controls">
                    {['name', 'email', 'created'].map(field => (
                        <button
                            key={field}
                            onClick={() => handleSortChange(field)}
                            className={`sort-btn ${sortBy === field ? 'active' : ''}`}
                        >
                            {field}
                            {sortBy === field && (
                                <span className="sort-indicator">
                                    {sortOrder === 'asc' ? '↑' : '↓'}
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>
            
            <div className="user-grid">
                {filteredAndSortedUsers.map(user => (
                    <UserCard
                        key={user.id}
                        user={user}
                        onClick={() => onUserSelect(user)}
                    />
                ))}
            </div>
            
            {filteredAndSortedUsers.length === 0 && (
                <div className="no-results">
                    Пользователи не найдены
                </div>
            )}
        </div>
    );
};

export default UserList;
```

## 🎨 CSS примеры

### Современный CSS с переменными

```css
/* CSS переменные и современный дизайн */
:root {
    /* Цветовая палитра */
    --primary-50: #eff6ff;
    --primary-100: #dbeafe;
    --primary-500: #3b82f6;
    --primary-600: #2563eb;
    --primary-900: #1e3a8a;
    
    /* Градиенты */
    --gradient-primary: linear-gradient(135deg, var(--primary-500), var(--primary-600));
    --gradient-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    /* Типографика */
    --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
    
    /* Отступы */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 1rem;
    --space-lg: 1.5rem;
    --space-xl: 2rem;
    
    /* Радиусы */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    
    /* Тени */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}

/* Компонент карточки */
.card {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
    padding: var(--space-lg);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    /* Grid layout */
    display: grid;
    gap: var(--space-md);
    
    /* Состояния */
    &:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
    }
    
    &:focus-within {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
}

/* Заголовок карточки */
.card__title {
    font-family: var(--font-sans);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary-900);
    margin: 0;
    
    /* Обрезание длинного текста */
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Гибкий grid layout */
.grid-responsive {
    display: grid;
    gap: var(--space-lg);
    
    /* Автоматическая адаптация колонок */
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    
    /* Медиа-запросы */
    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: var(--space-md);
    }
}

/* Кнопка с анимациями */
.button {
    /* Базовые стили */
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--space-sm);
    
    padding: var(--space-sm) var(--space-lg);
    border: none;
    border-radius: var(--radius-md);
    
    font-family: var(--font-sans);
    font-weight: 500;
    text-decoration: none;
    
    cursor: pointer;
    transition: all 0.2s ease;
    
    /* Варианты */
    &--primary {
        background: var(--gradient-primary);
        color: white;
        
        &:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }
        
        &:active {
            transform: translateY(0);
        }
    }
    
    &--outline {
        background: transparent;
        color: var(--primary-600);
        border: 2px solid var(--primary-500);
        
        &:hover {
            background: var(--primary-50);
        }
    }
    
    /* Состояния */
    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none !important;
    }
    
    &:focus-visible {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }
}

/* Анимация загрузки */
.loading-spinner {
    width: 2rem;
    height: 2rem;
    border: 2px solid var(--primary-100);
    border-top: 2px solid var(--primary-500);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Темная тема */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-primary: #1f2937;
        --bg-secondary: #374151;
        --text-primary: #f9fafb;
        --text-secondary: #d1d5db;
    }
    
    .card {
        background: var(--bg-secondary);
        color: var(--text-primary);
    }
}
```

## 🗄️ SQL примеры

### Сложные запросы

```sql
-- Аналитический запрос с оконными функциями
WITH monthly_stats AS (
    SELECT 
        DATE_TRUNC('month', order_date) as month,
        user_id,
        COUNT(*) as orders_count,
        SUM(total_amount) as total_spent,
        AVG(total_amount) as avg_order_value
    FROM orders 
    WHERE order_date >= '2024-01-01'
        AND status IN ('completed', 'delivered')
    GROUP BY DATE_TRUNC('month', order_date), user_id
),
user_rankings AS (
    SELECT 
        month,
        user_id,
        orders_count,
        total_spent,
        avg_order_value,
        
        -- Ранжирование пользователей по тратам
        ROW_NUMBER() OVER (
            PARTITION BY month 
            ORDER BY total_spent DESC
        ) as spending_rank,
        
        -- Процентиль по количеству заказов
        PERCENT_RANK() OVER (
            PARTITION BY month 
            ORDER BY orders_count
        ) as order_percentile,
        
        -- Сравнение с предыдущим месяцем
        LAG(total_spent) OVER (
            PARTITION BY user_id 
            ORDER BY month
        ) as prev_month_spent,
        
        -- Нарастающий итог
        SUM(total_spent) OVER (
            PARTITION BY user_id 
            ORDER BY month 
            ROWS UNBOUNDED PRECEDING
        ) as cumulative_spent
    FROM monthly_stats
)
SELECT 
    u.username,
    ur.month,
    ur.orders_count,
    ur.total_spent,
    ur.avg_order_value,
    ur.spending_rank,
    ROUND(ur.order_percentile * 100, 2) as order_percentile_pct,
    
    -- Изменение по сравнению с предыдущим месяцем
    CASE 
        WHEN ur.prev_month_spent IS NULL THEN 'Новый клиент'
        WHEN ur.total_spent > ur.prev_month_spent THEN 'Рост'
        WHEN ur.total_spent < ur.prev_month_spent THEN 'Снижение'
        ELSE 'Стабильно'
    END as trend,
    
    -- Процент изменения
    CASE 
        WHEN ur.prev_month_spent IS NOT NULL AND ur.prev_month_spent > 0 
        THEN ROUND(
            ((ur.total_spent - ur.prev_month_spent) / ur.prev_month_spent) * 100, 
            2
        )
        ELSE NULL
    END as change_percent,
    
    ur.cumulative_spent
FROM user_rankings ur
JOIN users u ON ur.user_id = u.id
WHERE ur.spending_rank <= 10  -- Топ-10 клиентов по тратам
ORDER BY ur.month DESC, ur.spending_rank;
```

## 🔄 Diff блоки

### Рефакторинг Python функции

```diff-python
class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url
-        self.session = requests.Session()
+        self.session = self._create_session()
+        self.retry_count = 3
+        self.timeout = 30
    
+    def _create_session(self):
+        """Создает настроенную сессию с retry логикой."""
+        session = requests.Session()
+        
+        # Настройка повторных попыток
+        retry_strategy = Retry(
+            total=self.retry_count,
+            status_forcelist=[429, 500, 502, 503, 504],
+            method_whitelist=["HEAD", "GET", "OPTIONS"],
+            backoff_factor=1
+        )
+        
+        adapter = HTTPAdapter(max_retries=retry_strategy)
+        session.mount("http://", adapter)
+        session.mount("https://", adapter)
+        
+        return session
    
    def get(self, endpoint, **kwargs):
        """Выполняет GET запрос к API."""
-        response = self.session.get(f"{self.base_url}{endpoint}")
-        return response.json()
+        try:
+            response = self.session.get(
+                f"{self.base_url}{endpoint}",
+                timeout=self.timeout,
+                **kwargs
+            )
+            response.raise_for_status()
+            return response.json()
+        except requests.exceptions.RequestException as e:
+            logger.error(f"API request failed: {e}")
+            raise APIException(f"Failed to fetch {endpoint}: {str(e)}")
```

### Обновление React хука

```diff-javascript
-import { useState, useEffect } from 'react';
+import { useState, useEffect, useCallback, useRef } from 'react';

-function useApi(url) {
+function useApi(url, options = {}) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
+    const [retry, setRetry] = useState(0);
+    const abortControllerRef = useRef(null);
+    
+    const { 
+        autoFetch = true, 
+        dependencies = [], 
+        retryLimit = 3 
+    } = options;

-    useEffect(() => {
+    const fetchData = useCallback(async () => {
+        // Отменяем предыдущий запрос
+        if (abortControllerRef.current) {
+            abortControllerRef.current.abort();
+        }
+        
+        abortControllerRef.current = new AbortController();
        setLoading(true);
        setError(null);
        
-        fetch(url)
-            .then(response => response.json())
-            .then(data => {
+        try {
+            const response = await fetch(url, {
+                signal: abortControllerRef.current.signal
+            });
+            
+            if (!response.ok) {
+                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
+            }
+            
+            const result = await response.json();
+            setData(result);
+            setError(null);
+        } catch (err) {
+            if (err.name !== 'AbortError') {
+                setError(err.message);
                setData(null);
-                setLoading(false);
-                setData(data);
-            })
-            .catch(err => {
-                setError(err.message);
-                setLoading(false);
-            });
-    }, [url]);
+            }
+        } finally {
+            setLoading(false);
+        }
+    }, [url]);
+    
+    const refetch = useCallback(() => {
+        setRetry(prev => prev + 1);
+    }, []);
+    
+    useEffect(() => {
+        if (autoFetch) {
+            fetchData();
+        }
+        
+        return () => {
+            if (abortControllerRef.current) {
+                abortControllerRef.current.abort();
+            }
+        };
+    }, [fetchData, retry, ...dependencies]);
+    
+    // Автоматический повтор при ошибке
+    useEffect(() => {
+        if (error && retry < retryLimit) {
+            const timer = setTimeout(() => {
+                refetch();
+            }, Math.pow(2, retry) * 1000); // Экспоненциальная задержка
+            
+            return () => clearTimeout(timer);
+        }
+    }, [error, retry, retryLimit, refetch]);

-    return { data, loading, error };
+    return { 
+        data, 
+        loading, 
+        error, 
+        refetch, 
+        retry: retry,
+        canRetry: retry < retryLimit
+    };
}
```

### Миграция CSS на современный синтаксис

```diff-css
/* Переход с флексбокса на Grid */
.container {
-    display: flex;
-    flex-wrap: wrap;
-    justify-content: space-between;
-    align-items: flex-start;
+    display: grid;
+    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
+    gap: 1.5rem;
+    align-items: start;
}

-.item {
-    flex: 1 1 300px;
-    margin: 0.75rem;
-    min-height: 200px;
-}
+.item {
+    min-height: 200px;
+    /* margin больше не нужен благодаря grid gap */
+}

/* Обновление цветов на CSS переменные */
.button {
-    background-color: #3498db;
-    border: 1px solid #2980b9;
-    color: #ffffff;
+    background-color: var(--color-primary);
+    border: 1px solid var(--color-primary-dark);
+    color: var(--color-white);
    
    /* Добавление современных возможностей */
+    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
+    transform: translateY(0);
}

.button:hover {
-    background-color: #2980b9;
+    background-color: var(--color-primary-dark);
+    transform: translateY(-2px);
+    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Добавление темной темы */
+@media (prefers-color-scheme: dark) {
+    :root {
+        --color-primary: #60a5fa;
+        --color-primary-dark: #3b82f6;
+        --color-white: #f8fafc;
+        --color-bg: #1e293b;
+        --color-text: #e2e8f0;
+    }
+    
+    body {
+        background-color: var(--color-bg);
+        color: var(--color-text);
+    }
+}
```

### Обновление SQL схемы

```diff-sql
-- Добавление новых полей и индексов
ALTER TABLE users 
-ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
+ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
+ADD COLUMN last_login_at TIMESTAMP NULL,
+ADD COLUMN login_attempts INT DEFAULT 0,
+ADD COLUMN is_locked BOOLEAN DEFAULT FALSE,
+ADD COLUMN profile_data JSONB DEFAULT '{}';

+-- Создание составного индекса для поиска
+CREATE INDEX CONCURRENTLY idx_users_search 
+ON users USING gin((
+    setweight(to_tsvector('russian', coalesce(name, '')), 'A') ||
+    setweight(to_tsvector('russian', coalesce(email, '')), 'B')
+));

+-- Добавление ограничений
+ALTER TABLE users 
+ADD CONSTRAINT chk_email_format 
+CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

+-- Создание функции для обновления updated_at
+CREATE OR REPLACE FUNCTION update_updated_at_column()
+RETURNS TRIGGER AS $$
+BEGIN
+    NEW.updated_at = CURRENT_TIMESTAMP;
+    RETURN NEW;
+END;
+$$ language 'plpgsql';

+-- Создание триггера
+CREATE TRIGGER update_users_updated_at 
+    BEFORE UPDATE ON users 
+    FOR EACH ROW 
+    EXECUTE FUNCTION update_updated_at_column();
```

---

## ✅ Заключение

Этот файл демонстрирует:

- **Python**: классы, асинхронный код, типизация
- **JavaScript**: ES6+, React, современные паттерны  
- **CSS**: переменные, Grid, анимации, темная тема
- **SQL**: сложные запросы, оконные функции, CTE
- **Diff блоки**: рефакторинг, миграции, улучшения

> [!info]
> Все примеры показывают современные best practices и паттерны разработки

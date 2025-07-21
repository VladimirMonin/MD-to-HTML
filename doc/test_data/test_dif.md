## Примеры Diff-блоков для тестирования

### HTML: Изменение атрибута

В этом примере мы меняем атрибут `class` у тега `div`.

```diff
- <div class="container">
+ <div class="container-fluid">
  <p>Какой-то текст.</p>
</div>
```

### HTML: Добавление нового элемента

Здесь мы добавляем новый пункт в навигационное меню.

```diff
<nav>
  <ul>
    <li><a href="/">Главная</a></li>
-   <li><a href="/about">О нас</a></li>
+   <li><a href="/about">О компании</a></li>
+   <li><a href="/contacts">Контакты</a></li>
  </ul>
</nav>
```

### CSS: Изменение цвета фона

Простой пример изменения значения свойства `background-color`.

```diff
body {
-  background-color: #fff;
+  background-color: #f0f2f5;
  font-family: "Roboto", sans-serif;
}
```

### CSS: Рефакторинг селектора

В этом примере мы делаем селектор более специфичным.

```diff
- .card {
+ .content .card {
  border: 1px solid #ccc;
  border-radius: 8px;
}
```

### CSS: Добавление вендорных префиксов

Пример добавления префиксов для кросс-браузерной совместимости.

```diff
.box {
-  transition: transform 0.3s ease;
+  -webkit-transition: transform 0.3s ease;
+  -moz-transition: transform 0.3s ease;
+  transition: transform 0.3s ease;
}
```

### JavaScript: Замена `var` на `let` и `const`

Классический пример модернизации старого JS-кода.

```diff
- var x = 10;
- var y = 20;
+ const x = 10;
+ let y = 20;
```

### JavaScript: Использование стрелочной функции

Рефакторинг анонимной функции в более короткую стрелочную.

```diff
- document.addEventListener('click', function() {
-   console.log('Clicked!');
- });
+ document.addEventListener('click', () => console.log('Clicked!'));
```

### JavaScript: Рефакторинг с `async/await`

Преобразование колбэков или промисов в синтаксис `async/await`.

```diff
- function fetchData() {
-   return fetch('/api/data').then(res => res.json());
- }
+ async function fetchData() {
+   const response = await fetch('/api/data');
+   const data = await response.json();
+   return data;
+ }
```

### Python: Изменение списка

Добавление нового элемента в список.

```diff
- allowed_users = ['admin', 'moderator']
+ allowed_users = ['admin', 'moderator', 'editor']
```

### Python: Улучшение comprehensions

Замена цикла на более идиоматичный list comprehension.

```diff
- squares = []
- for i in range(10):
-   squares.append(i * i)
+ squares = [i * i for i in range(10)]
```

### Python: Рефакторинг функции

Добавление аннотации типов и изменение возвращаемого значения.

```diff
- def get_user(id):
-   return db.get(id)
+ def get_user(user_id: int) -> User:
+   """Получает пользователя по ID."""
+   return db.query(User).filter_by(id=user_id).first()
```

### SQL: Добавление нового поля в выборку

Просто добавляем еще одну колонку в `SELECT`.

```diff
SELECT
  id,
-  name
+  name,
+  email
FROM users;
```

### SQL: Изменение условия `WHERE`

Пример изменения фильтрации для выборки активных пользователей.

```diff
SELECT *
FROM users
- WHERE status = 'active';
+ WHERE is_active = TRUE AND last_login > '2023-01-01';
```

### SQL: Добавление `JOIN`

Усложнение запроса для получения данных из связанной таблицы.

```diff
SELECT
  u.name,
-  u.role
+  r.name as role_name
FROM users u
+ JOIN roles r ON u.role_id = r.id;
```

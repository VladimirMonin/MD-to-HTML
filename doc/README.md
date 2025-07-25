# MD to HTML Конвертер

## Обзор

MD to HTML — это инструмент для преобразования Markdown-документов в красиво оформленные HTML-страницы с интерактивными элементами и параллакс-эффектами. Программа придаёт документам профессиональный вид и улучшает восприятие информации пользователями.

## Особенности

- **Современный дизайн** с использованием Bootstrap 5
- **Автоматическое оглавление** с подсветкой текущего раздела при прокрутке
- **Параллакс-эффект** с плавающими тематическими иконками
- **Подсветка синтаксиса** для кода с помощью highlight.js
- **Кнопки копирования кода** с анимацией
- **Полноэкранный просмотр изображений** по клику
- **Специальные блоки уведомлений** различных типов
- **Поддержка диаграмм Mermaid** для визуализации данных
- **Отображение сравнения кода (Diff)** для отслеживания изменений
- **Встроенный видеоплеер** с поддержкой HTML5 видео
- **Адаптивный дизайн** для всех устройств

## Структура проекта

```
MD_to_HTML/
├── assets/
│   ├── css/
│   │   ├── default.css       # Основные стили
│   │   └── parallax.css      # Стили для параллакс-эффекта
│   ├── js/
│   │   ├── codeCopy.js       # Функционал копирования кода
│   │   ├── main.js           # Основной JavaScript
│   │   ├── media.js          # Обработка медиа-контента
│   │   ├── menu.js           # Генерация оглавления
│   │   └── parallax.js       # Эффект параллакса
│   └── img/                  # Директория для изображений (опционально)
├── main.html                 # Шаблон HTML
└── .gitignore                # Игнорируемые файлы
```

## Как работает конвертация

Программа работает на основе шаблона `main.html`, в который подставляется преобразованный Markdown-контент. Для корректной работы в шаблоне используются следующие переменные:

- `{title}` — заголовок HTML-страницы
- `{brand}` — путь к изображению для фона заголовка (опционально)
- `{header}` — текст основного заголовка
- `{{ content }}` — место вставки преобразованного Markdown-контента

## Специальные блоки

MD to HTML поддерживает несколько типов специальных блоков для расширения функциональности стандартного Markdown.

### Блоки уведомлений

Для привлечения внимания к важной информации используются блоки уведомлений:

```markdown
> [!info]
> Это информационный блок

> [!warning]
> Это блок предупреждения

> [!success]
> Это блок успешного действия

> [!error]
> Это блок ошибки

> [!tip]
> Это блок полезного совета

> [!highlight]
> Это блок для выделения важной информации

> [!danger]
> Это блок для обозначения опасности
```

### Диаграммы Mermaid

Конвертер поддерживает рендеринг диаграмм и графиков с помощью Mermaid.js. Просто оберните ваш код Mermaid в блок с языком `mermaid`.

**Пример:**

```mermaid
graph TD;
    A[Начало] --> B{Условие};
    B -- Да --> C[Действие 1];
    B -- Нет --> D[Действие 2];
    C --> E[Конец];
    D --> E[Конец];
```

### Сравнение кода (Diff)

Для наглядного сравнения двух версий кода используйте специальный синтаксис `diff-язык`. Блок будет разделен на две части: «до» и «после». Зеленым цветом выделены добавленные строки, красным — удаленные.

![Пример Diff блока](images/diff_sample.png)

**Пример:**

````markdown
```diff-python
def greet(name):
-    print(f"Hello, {name}!")
+    # Приветствие с дополнительной проверкой
+    if name:
+        print(f"Welcome, {name}!")
+    else:
+        print("Hello, guest!")
```

````

## Параллакс-эффект

Для создания визуально привлекательного фона используется скрипт `parallax.js`, который генерирует анимированные иконки, плавающие на заднем плане страницы. Эффект поддерживает:

- Автоматический подбор иконок из библиотеки Bootstrap Icons
- Плавное движение иконок
- Отклик на скроллинг
- Настройка размеров, цветов и размытия

## Работа с изображениями и видео

- **Изображения**: при клике открываются в полноэкранном режиме через функционал в `media.js`
- **Видео**: автоматически подключаются к плееру Plyr для улучшенного воспроизведения

## Кастомизация

### Изменение стилей

Вы можете настроить внешний вид HTML-страниц, модифицируя CSS-файлы:

- `default.css` — основные стили страницы
- `parallax.css` — стили для параллакс-эффекта

### Изменение поведения JavaScript

Для изменения функциональности страницы, редактируйте соответствующие JS-файлы:

- `main.js` — основные функции и инициализация
- `codeCopy.js` — функционал копирования кода
- `media.js` — обработка мультимедиа
- `menu.js` — генерация и поведение оглавления
- `parallax.js` — эффект параллакса с плавающими иконками

### Изменение HTML-шаблона

Шаблон находится в файле `main.html`. При его модификации обратите внимание на переменные, которые заменяются при конвертации (`{title}`, `{brand}`, `{header}`, `{{ content }}`).

## Требования

- Современный браузер с поддержкой JavaScript
- Bootstrap 5
- Highlight.js
- Plyr (для видео)
- Mermaid.js (для диаграмм)
- Bootstrap Icons

document.addEventListener("DOMContentLoaded", function () {
  // =========================
  // Параметры и настройки эффекта
  // =========================

  // Диапазон количества фигур при старте
  const NUM_SHAPES_MIN = 40; // минимальное число фигур
  const NUM_SHAPES_MAX = 60; // максимальное число фигур

  // Диапазон размеров фигур (в rem)
  const MIN_SIZE = 2; // минимальный размер фигуры (rem)
  const MAX_SIZE = 7; // максимальный размер фигуры (rem)

  // Диапазон размытия (blur) для фигур (в пикселях)
  const MIN_BLUR = 3; // минимальное значение blur (px)
  const MAX_BLUR = 5; // максимальное значение blur (px)
  const EXTRA_BLUR = 2; // дополнительное блюр для мест под подложкой

  // Настройки движения фигур
  const BASE_SPEED_RANGE = 40; // базовый диапазон скорости
  const FRICTION = 0.99; // коэффициент фрикции (замедление)
  const SCROLL_ACCEL_FACTOR = 0.003; // коэффициент ускорения при скролле

  // Ограничение максимальной скорости (px/с)
  const MAX_SPEED = 100;

  // Настройки отталкивания между фигурами
  const REPEL_THRESHOLD = 100; // расстояние, при котором начинается отталкивание (px)
  const REPEL_FACTOR = 300; // сила отталкивания

  // Настройки "невидимых стен"
  const WALL_MARGIN = 50; // отступ (px) от краёв экрана для "стен"

  // Массив иконок (классы из Bootstrap Icons)
  const shapesIcons = [
    "bi-robot",
    "bi-cpu",
    "bi-laptop",
    "bi-display",
    "bi-code-slash",
    "bi-terminal-fill",
    "bi-gear-fill",
    "bi-arrow-repeat",
    "bi-file-earmark-code",
    "bi-bug-fill",
    "bi-lightning-fill",
    "bi-diagram-3",
  ];

  // Получаем размер вьюпорта
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  // Количество фигур, генерируем по диапазону
  const shapesCount =
    Math.floor(Math.random() * (NUM_SHAPES_MAX - NUM_SHAPES_MIN + 1)) +
    NUM_SHAPES_MIN;

  // Контейнер для параллакс-иконок
  const parallaxContainer = document.createElement("div");
  parallaxContainer.classList.add("parallax-bg");
  document.body.insertBefore(parallaxContainer, document.body.firstChild);

  // Массив с объектами-иконками
  const shapes = [];

  // Получаем область подложки для основного текста
  const contentArea = document.querySelector(".content-wrapper");

  // Генерация фигур
  for (let i = 0; i < shapesCount; i++) {
    const shapeElement = document.createElement("i");
    shapeElement.classList.add(
      "bi",
      shapesIcons[Math.floor(Math.random() * shapesIcons.length)],
      "parallax-shape"
    );

    // Случайное начальное положение в процентах
    const topPercent = Math.random() * 100;
    const leftPercent = Math.random() * 100;
    shapeElement.style.top = topPercent + "%";
    shapeElement.style.left = leftPercent + "%";

    // Вычисляем начальные абсолютные координаты
    const initX = (leftPercent / 100) * viewportWidth;
    const initY = (topPercent / 100) * viewportHeight;

    // Случайный размер фигуры
    const size = (Math.random() * (MAX_SIZE - MIN_SIZE) + MIN_SIZE).toFixed(2);
    shapeElement.style.fontSize = size + "rem";

    // Генерируем базовое значение blur
    const baseBlur = parseFloat(
      (Math.random() * (MAX_BLUR - MIN_BLUR) + MIN_BLUR).toFixed(1)
    );
    shapeElement.style.filter = `blur(${baseBlur}px)`;

    // Случайный цвет фигуры:
    // С вероятностью 30% выбираем тёплый оттенок (hue от 20 до 60), иначе произвольный от 0 до 360
    let hue =
      Math.random() < 0.3
        ? Math.floor(Math.random() * 40) + 20
        : Math.floor(Math.random() * 360);
    shapeElement.style.color = `hsl(${hue}, 60%, 60%)`;

    // Случайный угол поворота (от 0 до 360 градусов)
    const rotation = Math.floor(Math.random() * 361);

    // Объект с параметрами движения фигуры
    const shapeObj = {
      element: shapeElement,
      posX: 0, // смещение по X относительно начальной позиции
      posY: 0, // смещение по Y относительно начальной позиции
      initX: initX, // начальная абсолютная координата X
      initY: initY, // начальная абсолютная координата Y
      speedX: (Math.random() - 0.5) * BASE_SPEED_RANGE, // базовая скорость по X
      speedY: (Math.random() - 0.5) * BASE_SPEED_RANGE, // базовая скорость по Y
      baseBlur: baseBlur, // базовый blur
      rotation: rotation, // начальный угол поворота
    };

    parallaxContainer.appendChild(shapeElement);
    shapes.push(shapeObj);
  }

  // Переменные времени и скролла
  let lastScroll = window.scrollY;
  let lastTime = performance.now();

  // Функция обновления анимации
  function update() {
    const now = performance.now();
    const dt = (now - lastTime) / 1000; // интервал времени в секундах
    const currentScroll = window.scrollY;
    const scrollDelta = Math.abs(currentScroll - lastScroll);
    const contentRect = contentArea
      ? contentArea.getBoundingClientRect()
      : null;

    // Отталкивание между фигурами
    for (let i = 0; i < shapes.length; i++) {
      for (let j = i + 1; j < shapes.length; j++) {
        const dx =
          shapes[j].initX + shapes[j].posX - (shapes[i].initX + shapes[i].posX);
        const dy =
          shapes[j].initY + shapes[j].posY - (shapes[i].initY + shapes[i].posY);
        const distance = Math.hypot(dx, dy);
        if (distance < REPEL_THRESHOLD && distance > 0) {
          const force =
            (REPEL_FACTOR * (REPEL_THRESHOLD - distance)) / REPEL_THRESHOLD;
          const nx = dx / distance;
          const ny = dy / distance;
          shapes[i].speedX -= nx * force * dt;
          shapes[i].speedY -= ny * force * dt;
          shapes[j].speedX += nx * force * dt;
          shapes[j].speedY += ny * force * dt;
        }
      }
    }

    // При изменении скролла ускоряем фигуры без изменения направления
    if (scrollDelta > 0) {
      const accel = 1 + scrollDelta * SCROLL_ACCEL_FACTOR;
      shapes.forEach((shape) => {
        shape.speedX *= accel;
        shape.speedY *= accel;
      });
    }

    // Обновление позиции и отображение каждой фигуры
    shapes.forEach((shape) => {
      // Применяем фрикцию
      shape.speedX *= FRICTION;
      shape.speedY *= FRICTION;

      // Ограничение максимальной скорости
      const currentSpeed = Math.hypot(shape.speedX, shape.speedY);
      if (currentSpeed > MAX_SPEED) {
        const ratio = MAX_SPEED / currentSpeed;
        shape.speedX *= ratio;
        shape.speedY *= ratio;
      }

      // Обновляем смещение
      shape.posX += shape.speedX * dt;
      shape.posY += shape.speedY * dt;

      // Вычисляем текущее абсолютное положение фигуры
      let currentX = shape.initX + shape.posX;
      let currentY = shape.initY + shape.posY;

      // Отражение от невидимых стен (с отступом WALL_MARGIN)
      if (currentX < WALL_MARGIN) {
        shape.posX = WALL_MARGIN - shape.initX;
        shape.speedX = -shape.speedX;
      } else if (currentX > viewportWidth - WALL_MARGIN) {
        shape.posX = viewportWidth - WALL_MARGIN - shape.initX;
        shape.speedX = -shape.speedX;
      }
      if (currentY < WALL_MARGIN) {
        shape.posY = WALL_MARGIN - shape.initY;
        shape.speedY = -shape.speedY;
      } else if (currentY > viewportHeight - WALL_MARGIN) {
        shape.posY = viewportHeight - WALL_MARGIN - shape.initY;
        shape.speedY = -shape.speedY;
      }

      // Определяем уровень blur, применяя блюр подложки, если фигура целиком под ней
      let currentBlur = shape.baseBlur;
      if (contentRect) {
        const shapeRect = shape.element.getBoundingClientRect();
        if (
          shapeRect.top >= contentRect.top &&
          shapeRect.left >= contentRect.left &&
          shapeRect.bottom <= contentRect.bottom &&
          shapeRect.right <= contentRect.right
        ) {
          currentBlur = shape.baseBlur + EXTRA_BLUR;
        }
      }
      shape.element.style.filter = `blur(${currentBlur}px)`;

      // Применяем смещение и постоянный угол поворота
      shape.element.style.transform = `translate(${shape.posX}px, ${shape.posY}px) rotate(${shape.rotation}deg)`;
    });

    lastScroll = currentScroll;
    lastTime = now;
    requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
});

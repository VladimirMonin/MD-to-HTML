document.addEventListener("DOMContentLoaded", function () {
  // Создаём контейнер для параллакс-эффекта
  const parallaxContainer = document.createElement("div");
  parallaxContainer.classList.add("parallax-bg");
  document.body.insertBefore(parallaxContainer, document.body.firstChild);

  // Массив классов BS5-иконок (убедитесь, что эти иконки доступны)
  const shapesIcons = [
    "bi-square",
    "bi-circle-fill",
    "bi-diamond-fill",
    "bi-triangle-fill",
  ];

  // Увеличиваем количество фигур: от 10 до 20
  const shapesCount = Math.floor(Math.random() * 11) + 10;

  // Массив для хранения созданных фигур
  const shapes = [];

  for (let i = 0; i < shapesCount; i++) {
    const shape = document.createElement("i");
    shape.classList.add(
      "bi",
      shapesIcons[Math.floor(Math.random() * shapesIcons.length)],
      "parallax-shape"
    );

    // Случайные позиция в процентах
    const topPos = Math.random() * 100;
    const leftPos = Math.random() * 100;
    shape.style.top = topPos + "%";
    shape.style.left = leftPos + "%";

    // Сохраняем исходные координаты в data-атрибутах (если потребуется для более сложных расчётов)
    shape.dataset.baseTop = topPos;
    shape.dataset.baseLeft = leftPos;

    // Задаём случайный цвет через HSL
    const hue = Math.floor(Math.random() * 360);
    shape.style.color = `hsl(${hue}, 60%, 60%)`;

    // Назначаем индивидуальные коэффициенты смещения по оси X и Y для параллакс-эффекта
    // Диапазон от -0.3 до 0.3
    shape.dataset.speedX = (Math.random() - 0.5) * 0.6;
    shape.dataset.speedY = (Math.random() - 0.5) * 0.6;

    parallaxContainer.appendChild(shape);
    shapes.push(shape);
  }

  // Обновление позиций фигур при скролле страницы
  window.addEventListener("scroll", () => {
    const scrollY = window.scrollY;
    shapes.forEach((shape) => {
      const speedX = parseFloat(shape.dataset.speedX);
      const speedY = parseFloat(shape.dataset.speedY);
      const translateX = scrollY * speedX;
      const translateY = scrollY * speedY;
      shape.style.transform = `translate(${translateX}px, ${translateY}px)`;
    });
  });
});

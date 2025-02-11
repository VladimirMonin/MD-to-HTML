document.addEventListener("DOMContentLoaded", function () {
  // Создаём контейнер для параллакс-эффекта
  const parallaxContainer = document.createElement("div");
  parallaxContainer.classList.add("parallax-bg");
  document.body.insertBefore(parallaxContainer, document.body.firstChild);

  // Массив классов BS5-иконок (убедитесь, что эти иконки существуют в Bootstrap Icons)
  const shapesIcons = [
    "bi-square",
    "bi-circle-fill",
    "bi-diamond-fill",
    "bi-triangle-fill",
  ];

  // Количество фигур можно регулировать – здесь создаём случайное количество от 4 до 8
  const shapesCount = Math.floor(Math.random() * 5) + 4;

  for (let i = 0; i < shapesCount; i++) {
    const shape = document.createElement("i");
    shape.classList.add(
      "bi",
      shapesIcons[Math.floor(Math.random() * shapesIcons.length)],
      "parallax-shape"
    );

    // Задаём случайные позицию и размер
    shape.style.top = Math.random() * 100 + "%";
    shape.style.left = Math.random() * 100 + "%";

    // Рандомное значение для цвета через HSL
    shape.style.color = `hsl(${Math.floor(Math.random() * 360)}, 60%, 60%)`;

    // Рандомное изменение длительности и задержки анимации
    shape.style.animationDuration = 5 + Math.random() * 5 + "s";
    shape.style.animationDelay = Math.random() * 2 + "s";

    parallaxContainer.appendChild(shape);
  }
});

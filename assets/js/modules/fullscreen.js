/**
 * Fullscreen Media (Images & SVG) - ES6 Module
 * Поддержка полноэкранного просмотра изображений и Mermaid диаграмм
 */

let _fullscreenContainer = null;

function createFullscreenContainer() {
  const container = document.createElement("div");
  container.classList.add("fullscreen-container");
  container.id = "fullscreen-container-singleton";

  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = "✕";
  closeBtn.classList.add("fullscreen-close-btn");
  closeBtn.title = "Close (ESC)";
  closeBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    container.classList.remove("active");
  });

  container.appendChild(closeBtn);
  return container;
}

function showFullscreenContent(content) {
  if (!_fullscreenContainer) {
    console.error("Fullscreen container not initialized");
    return;
  }

  // Удаляем предыдущий контент
  const existingContent = _fullscreenContainer.querySelector(
    "img, .fullscreen-svg-wrapper"
  );
  if (existingContent) {
    existingContent.remove();
  }

  if (content.tagName === "IMG") {
    _fullscreenContainer.appendChild(content);
  } else if (content.tagName.toUpperCase() === "SVG") {
    const wrapper = document.createElement("div");
    wrapper.classList.add("fullscreen-svg-wrapper");

    // Инлайн-стили для гарантированной видимости
    wrapper.style.cssText =
      "background: #ffffff !important; padding: 2em !important; border-radius: 12px !important; width: 90vw !important; height: 85vh !important; display: flex !important; justify-content: center !important; align-items: center !important; box-shadow: 0 0 50px rgba(0,0,0,0.5) !important;";

    content.style.cssText =
      "width: 100% !important; height: 100% !important; max-width: none !important; max-height: none !important; display: block !important;";

    wrapper.appendChild(content);
    _fullscreenContainer.appendChild(wrapper);
  }

  _fullscreenContainer.classList.add("active");
}

function attachMermaidClickHandlers() {
  const mermaidContainers = document.querySelectorAll("div.mermaid, .mermaid");

  mermaidContainers.forEach((container) => {
    if (container.dataset.fullscreenAttached === "true") {
      return;
    }

    container.dataset.fullscreenAttached = "true";
    container.style.cursor = "zoom-in";

    container.addEventListener("click", function (e) {
      e.stopPropagation();
      e.preventDefault();

      const svg = this.querySelector("svg");
      if (!svg) return;

      // Клонируем через innerHTML для сохранения SVG namespace
      const tempWrapper = document.createElement("div");
      tempWrapper.innerHTML = svg.outerHTML;
      const svgClone = tempWrapper.firstElementChild;

      // Сохраняем или создаём viewBox
      const rect = svg.getBoundingClientRect();
      const existingViewBox = svg.getAttribute("viewBox");
      if (!existingViewBox) {
        svgClone.setAttribute("viewBox", `0 0 ${rect.width} ${rect.height}`);
      }

      // Удаляем фиксированные размеры
      svgClone.removeAttribute("width");
      svgClone.removeAttribute("height");
      svgClone.removeAttribute("style");

      showFullscreenContent(svgClone);
    });
  });
}

export function enableFullscreenMedia() {
  // Создаём контейнер
  _fullscreenContainer = createFullscreenContainer();
  document.body.appendChild(_fullscreenContainer);

  // Обработка изображений
  document.querySelectorAll("img:not(.no-fullscreen)").forEach((img) => {
    img.style.cursor = "zoom-in";
    img.addEventListener("click", () => {
      showFullscreenContent(img.cloneNode(true));
    });
  });

  // Обработка Mermaid диаграмм
  attachMermaidClickHandlers();

  // Observer для асинхронно отрендеренных диаграмм
  const observer = new MutationObserver(() => {
    attachMermaidClickHandlers();
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  // Останавливаем observer через 10 секунд
  setTimeout(() => observer.disconnect(), 10000);

  // Закрытие по клику на фон
  _fullscreenContainer.addEventListener("click", (e) => {
    if (e.target === _fullscreenContainer) {
      _fullscreenContainer.classList.remove("active");
    }
  });

  // Закрытие по ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      _fullscreenContainer.classList.remove("active");
    }
  });

  console.log("✅ Fullscreen media enabled");
}

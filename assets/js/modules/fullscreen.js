/**
 * Fullscreen Media (Images & SVG) - ES6 Module
 */

export function enableFullscreenMedia() {
  const fullscreenContainer = createFullscreenContainer();
  document.body.appendChild(fullscreenContainer);

  // Обработка изображений
  document.querySelectorAll("img:not(.no-fullscreen)").forEach((img) => {
    img.style.cursor = "zoom-in";
    img.addEventListener("click", () => {
      showFullscreenContent(fullscreenContainer, img.cloneNode(true));
    });
  });

  // Обработка Mermaid диаграмм
  attachMermaidClickHandlers(fullscreenContainer);

  const observer = new MutationObserver(() => {
    attachMermaidClickHandlers(fullscreenContainer);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  setTimeout(() => observer.disconnect(), 5000);

  // Закрытие
  fullscreenContainer.addEventListener("click", (e) => {
    if (e.target === fullscreenContainer) {
      fullscreenContainer.classList.remove("active");
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      fullscreenContainer.classList.remove("active");
    }
  });

  console.log("✅ Fullscreen media enabled");
}

function createFullscreenContainer() {
  const container = document.createElement("div");
  container.classList.add("fullscreen-container");

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

function showFullscreenContent(container, content) {
  const existingContent = container.querySelector(
    "img, .fullscreen-svg-wrapper"
  );
  if (existingContent) {
    existingContent.remove();
  }

  if (content.tagName === "IMG") {
    container.appendChild(content);
  } else if (content.tagName === "SVG") {
    const wrapper = document.createElement("div");
    wrapper.classList.add("fullscreen-svg-wrapper");
    wrapper.appendChild(content);
    container.appendChild(wrapper);
  }

  container.classList.add("active");
}

function attachMermaidClickHandlers(fullscreenContainer) {
  document.querySelectorAll("pre.mermaid svg, .mermaid svg").forEach((svg) => {
    if (svg.dataset.fullscreenAttached) return;
    svg.dataset.fullscreenAttached = "true";

    const parentPre = svg.closest("pre.mermaid, .mermaid");
    if (parentPre) {
      parentPre.style.cursor = "zoom-in";
      parentPre.addEventListener("click", () => {
        const svgClone = svg.cloneNode(true);
        showFullscreenContent(fullscreenContainer, svgClone);
      });
    }
  });
}

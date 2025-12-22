/**
 * Pandoc Book Enhancements
 * - Code copy buttons
 * - Fullscreen images and SVG diagrams (Mermaid)
 * - Smooth scroll for TOC links
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("📚 Book enhancements loaded");

  addCodeCopyButtons();
  enableFullscreenMedia();
  smoothScrollTOC();
  initDynamicBreadcrumbs();
});

// ===== CODE COPY BUTTONS =====

function addCodeCopyButtons() {
  document.querySelectorAll("pre:not(.mermaid)").forEach((preBlock) => {
    // Добавляем wrapper для позиционирования кнопки
    preBlock.style.position = "relative";

    const copyButton = createCopyButton();
    preBlock.appendChild(copyButton);

    copyButton.addEventListener("click", () => {
      const codeElement = preBlock.querySelector("code");
      if (!codeElement) return;

      const codeContent = codeElement.innerText;
      navigator.clipboard.writeText(codeContent).then(() => {
        showCopyFeedback(copyButton);
      });
    });
  });
  console.log("✅ Code copy buttons added");
}

function createCopyButton() {
  const btn = document.createElement("button");
  btn.innerHTML = "📋";
  btn.classList.add("code-copy-btn");
  btn.setAttribute("aria-label", "Copy code");
  btn.title = "Copy code";
  return btn;
}

function showCopyFeedback(button) {
  const originalHTML = button.innerHTML;
  button.innerHTML = "✅";
  button.style.color = "#4caf50";

  setTimeout(() => {
    button.innerHTML = originalHTML;
    button.style.color = "";
  }, 2000);
}

// ===== FULLSCREEN MEDIA (Images & SVG Diagrams) =====

function enableFullscreenMedia() {
  const fullscreenContainer = createFullscreenContainer();
  document.body.appendChild(fullscreenContainer);

  // Обработка обычных изображений
  document.querySelectorAll("img:not(.no-fullscreen)").forEach((img) => {
    img.style.cursor = "zoom-in";
    img.addEventListener("click", () => {
      showFullscreenContent(fullscreenContainer, img.cloneNode(true));
    });
  });

  // Обработка Mermaid диаграмм - нужно ждать пока Mermaid отрендерит SVG
  // Пробуем сразу и через observer
  attachMermaidClickHandlers(fullscreenContainer);

  // Наблюдаем за добавлением SVG (Mermaid рендерит асинхронно)
  const observer = new MutationObserver(() => {
    attachMermaidClickHandlers(fullscreenContainer);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });

  // Останавливаем observer через 5 секунд (все должно отрендериться)
  setTimeout(() => observer.disconnect(), 5000);

  // Закрытие по клику
  fullscreenContainer.addEventListener("click", (e) => {
    if (e.target === fullscreenContainer) {
      fullscreenContainer.classList.remove("active");
    }
  });

  // Закрытие по ESC
  document.addEventListener("keydown", (e) => {
    if (
      e.key === "Escape" &&
      fullscreenContainer.classList.contains("active")
    ) {
      fullscreenContainer.classList.remove("active");
    }
  });

  console.log("✅ Fullscreen media enabled");
}

// NOTE: attachMermaidClickHandlers удалена - используется версия из modules/fullscreen.js
// для избежания конфликтов и дублирования обработчиков

function createFullscreenContainer() {
  const container = document.createElement("div");
  container.classList.add("fullscreen-container");
  return container;
}

function showFullscreenContent(container, element) {
  container.innerHTML = "";

  // Добавляем кнопку закрытия
  const closeBtn = document.createElement("button");
  closeBtn.innerHTML = "✕";
  closeBtn.classList.add("fullscreen-close-btn");
  closeBtn.addEventListener("click", () => {
    container.classList.remove("active");
  });

  // Если это SVG (диаграмма), добавляем белый фон
  if (element.tagName === "svg") {
    const wrapper = document.createElement("div");
    wrapper.classList.add("fullscreen-svg-wrapper");
    wrapper.appendChild(element);
    container.appendChild(closeBtn);
    container.appendChild(wrapper);
  } else {
    // Для изображений - как обычно
    container.appendChild(closeBtn);
    container.appendChild(element);
  }

  container.classList.add("active");
}

// ===== SMOOTH SCROLL FOR TOC =====

function smoothScrollTOC() {
  document.querySelectorAll('#TOC a[href^="#"]').forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const targetId = link.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });
  console.log("✅ Smooth scroll enabled");
}

// ===== DYNAMIC BREADCRUMBS =====

function initDynamicBreadcrumbs() {
  // Создаем контейнер для хлебных крошек
  const breadcrumbsContainer = document.createElement("div");
  breadcrumbsContainer.className = "breadcrumbs-dynamic";
  document.body.insertBefore(breadcrumbsContainer, document.body.firstChild);

  const headings = Array.from(document.querySelectorAll("h2, h3"));
  if (headings.length === 0) {
    breadcrumbsContainer.style.display = "none";
    return;
  }

  // Добавляем ID к заголовкам (если нет)
  headings.forEach((heading, index) => {
    if (!heading.id) {
      const slug = heading.textContent
        .toLowerCase()
        .replace(/[^\w\s-]/g, "")
        .replace(/\s+/g, "-")
        .substring(0, 50);
      heading.id = `heading-${slug}-${index}`;
    }
  });

  const allH2 = headings.filter((h) => h.tagName === "H2");

  function updateBreadcrumbs() {
    const scrollPosition = window.scrollY + 150;

    let currentH2 = null;
    let currentH3 = null;

    for (const heading of headings) {
      const headingTop = heading.offsetTop;

      if (headingTop <= scrollPosition) {
        if (heading.tagName === "H2") {
          currentH2 = heading;
          currentH3 = null;
        } else if (heading.tagName === "H3" && currentH2) {
          currentH3 = heading;
        }
      }
    }

    breadcrumbsContainer.innerHTML = "";

    if (currentH2) {
      addBreadcrumbWithDropdown(breadcrumbsContainer, currentH2, allH2);
    }

    if (currentH3) {
      addBreadcrumb(
        breadcrumbsContainer,
        currentH3.textContent,
        currentH3.id,
        true,
        true // isH3 = true для скрытия на мобильных
      );
    }
  }

  function addBreadcrumbWithDropdown(container, currentH2, allH2) {
    const wrapper = document.createElement("span");
    wrapper.className = "breadcrumb-item breadcrumb-dropdown";

    const link = document.createElement("a");
    link.href = `#${currentH2.id}`;
    link.textContent = currentH2.textContent;
    link.className = "breadcrumb-h2-link";

    const dropdown = document.createElement("div");
    dropdown.className = "breadcrumb-dropdown-menu";

    allH2.forEach((h2) => {
      const dropdownItem = document.createElement("a");
      dropdownItem.href = `#${h2.id}`;
      dropdownItem.textContent = h2.textContent;
      dropdownItem.className = "breadcrumb-dropdown-item";

      if (h2.id === currentH2.id) {
        dropdownItem.classList.add("active");
      }

      dropdownItem.addEventListener("click", (e) => {
        e.preventDefault();
        h2.scrollIntoView({ behavior: "smooth", block: "start" });
        dropdown.classList.remove("show");
      });

      dropdown.appendChild(dropdownItem);
    });

    wrapper.appendChild(link);
    wrapper.appendChild(dropdown);

    let closeTimeout;
    let isTouchDevice = "ontouchstart" in window;

    // Desktop: hover для открытия
    wrapper.addEventListener("mouseenter", () => {
      if (!isTouchDevice) {
        clearTimeout(closeTimeout);
        dropdown.classList.add("show");
      }
    });

    wrapper.addEventListener("mouseleave", () => {
      if (!isTouchDevice) {
        // Задержка 300ms перед закрытием - дает время переместить мышь к меню
        closeTimeout = setTimeout(() => {
          dropdown.classList.remove("show");
        }, 300);
      }
    });

    // Mobile/Touch: клик/тап для toggle меню
    link.addEventListener("click", (e) => {
      e.preventDefault();

      if (isTouchDevice || window.innerWidth <= 768) {
        // На мобильных - toggle dropdown
        dropdown.classList.toggle("show");
      } else {
        // На desktop - переход к заголовку
        currentH2.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });

    // Закрытие dropdown при клике вне его
    document.addEventListener("click", (e) => {
      if (!wrapper.contains(e.target)) {
        dropdown.classList.remove("show");
      }
    });

    container.appendChild(wrapper);

    const separator = document.createElement("span");
    separator.className = "breadcrumb-separator";
    separator.textContent = " / ";
    container.appendChild(separator);
  }

  function addBreadcrumb(container, text, id, isLast = false, isH3 = false) {
    const item = document.createElement("span");
    item.className = "breadcrumb-item";

    // Добавляем класс для h3 элементов (для скрытия на мобильных)
    if (isH3) {
      item.classList.add("breadcrumb-h3");
    }

    if (isLast) {
      item.textContent = text;
      item.classList.add("active");
    } else {
      const link = document.createElement("a");
      link.href = `#${id}`;
      link.textContent = text;

      link.addEventListener("click", (e) => {
        e.preventDefault();
        const target = document.getElementById(id);
        if (target) {
          target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });

      item.appendChild(link);
    }

    container.appendChild(item);

    // Добавляем разделитель с классом для h3 (для скрытия на мобильных)
    if (isH3 && !isLast) {
      const separator = document.createElement("span");
      separator.className = "breadcrumb-separator h3-separator";
      separator.textContent = " / ";
      container.appendChild(separator);
    }
  }

  let ticking = false;
  window.addEventListener("scroll", () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        updateBreadcrumbs();
        ticking = false;
      });
      ticking = true;
    }
  });

  updateBreadcrumbs();
  console.log(
    `✅ Dynamic breadcrumbs initialized (${allH2.length} H2 headings)`
  );
}

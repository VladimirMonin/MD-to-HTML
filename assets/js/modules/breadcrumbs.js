/**
 * Dynamic Breadcrumbs - ES6 Module
 * Отслеживают текущий H2/H3 при прокрутке
 * Dropdown меню для навигации по всем H2
 */

export function initDynamicBreadcrumbs() {
  console.log("🔧 [Breadcrumbs] Инициализация...");
  
  const breadcrumbsContainer = document.querySelector(".breadcrumbs-dynamic");
  if (!breadcrumbsContainer) {
    console.warn("⚠️ [Breadcrumbs] Контейнер .breadcrumbs-dynamic не найден");
    return;
  }

  const headings = Array.from(document.querySelectorAll("h2, h3"));
  if (headings.length === 0) {
    console.warn("⚠️ [Breadcrumbs] Заголовки h2/h3 не найдены");
    return;
  }

  console.log(`📚 [Breadcrumbs] Найдено заголовков: ${headings.length} (h2: ${headings.filter(h => h.tagName === "H2").length}, h3: ${headings.filter(h => h.tagName === "H3").length})`);

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
  
  // Определяем устройство
  const isTouchDevice = 'ontouchstart' in window;
  const isMobile = window.innerWidth <= 768;
  console.log(`📱 [Breadcrumbs] Touch: ${isTouchDevice}, Mobile: ${isMobile}, Width: ${window.innerWidth}px`);

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
    
    console.log(`📍 [Breadcrumbs] Update - H2: ${currentH2 ? currentH2.textContent.substring(0,30) : 'none'}, H3: ${currentH3 ? currentH3.textContent.substring(0,30) : 'none'}`);

    if (currentH2) {
      addBreadcrumbWithDropdown(breadcrumbsContainer, currentH2, allH2);
    }

    if (currentH3) {
      console.log(`➕ [Breadcrumbs] Добавляем H3 элемент: "${currentH3.textContent.substring(0,30)}"`);
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

    let closeTimer;
    let isTouchDevice = 'ontouchstart' in window;
    let isMobile = window.innerWidth <= 768;
    
    console.log(`🔘 [Dropdown] Touch=${isTouchDevice}, Mobile=${isMobile}, Width=${window.innerWidth}px`);
    
    // Desktop: hover для открытия
    wrapper.addEventListener("mouseenter", () => {
      if (!isTouchDevice) {
        console.log("🖱️ [Dropdown] Hover - открываем меню");
        clearTimeout(closeTimer);
        dropdown.classList.add("show");
      } else {
        console.log("👆 [Dropdown] Hover игнорируется (touch device)");
      }
    });

    wrapper.addEventListener("mouseleave", () => {
      if (!isTouchDevice) {
        console.log("🖱️ [Dropdown] Mouseleave - закрываем через 300ms");
        closeTimer = setTimeout(() => {
          dropdown.classList.remove("show");
        }, 300);
      }
    });

    // Mobile/Touch: клик/тап для toggle меню
    link.addEventListener("click", (e) => {
      e.preventDefault();
      console.log(`👆 [Dropdown] Click - Touch=${isTouchDevice}, Mobile=${isMobile}`);
      
      if (isTouchDevice || window.innerWidth <= 768) {
        // На мобильных - toggle dropdown
        const isShown = dropdown.classList.toggle("show");
        console.log(`📲 [Dropdown] Toggle menu - теперь ${isShown ? 'ОТКРЫТО' : 'ЗАКРЫТО'}`);
      } else {
        // На desktop - переход к заголовку
        console.log("🖥️ [Dropdown] Desktop - скролл к заголовку");
        currentH2.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
    
    // Закрытие dropdown при клике вне его
    document.addEventListener("click", (e) => {
      if (!wrapper.contains(e.target)) {
        if (dropdown.classList.contains("show")) {
          console.log("❌ [Dropdown] Клик вне - закрываем");
          dropdown.classList.remove("show");
        }
      }
    });

    container.appendChild(wrapper);

    const separator = document.createElement("span");
    separator.className = "breadcrumb-separator h2-h3-separator";
    separator.textContent = " / ";
    container.appendChild(separator);
  }

  function addBreadcrumb(container, text, id, isLast = false, isH3 = false) {
    const item = document.createElement("span");
    item.className = "breadcrumb-item";
    
    // Добавляем класс для h3 элементов (для скрытия на мобильных)
    if (isH3) {
      item.classList.add("breadcrumb-h3");
      console.log(`🏷️ [Breadcrumb] Добавлен класс breadcrumb-h3 к: "${text.substring(0,30)}", классы: ${item.className}`);
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
      console.log(`🏷️ [Breadcrumb] Добавлен разделитель h3-separator`);
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

/**
 * Dynamic Breadcrumbs - ES6 Module
 * Отслеживают текущий H2/H3 при прокрутке
 * Dropdown меню для навигации по всем H2
 */

export function initDynamicBreadcrumbs() {
  const breadcrumbsContainer = document.querySelector(".breadcrumbs-dynamic");
  if (!breadcrumbsContainer) return;

  const headings = Array.from(document.querySelectorAll("h2, h3"));
  if (headings.length === 0) return;

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
        true
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
    wrapper.addEventListener("mouseenter", () => {
      clearTimeout(closeTimer);
      dropdown.classList.add("show");
    });

    wrapper.addEventListener("mouseleave", () => {
      closeTimer = setTimeout(() => {
        dropdown.classList.remove("show");
      }, 300);
    });

    link.addEventListener("click", (e) => {
      e.preventDefault();
      currentH2.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    container.appendChild(wrapper);

    const separator = document.createElement("span");
    separator.className = "breadcrumb-separator";
    separator.textContent = " / ";
    container.appendChild(separator);
  }

  function addBreadcrumb(container, text, id, isLast = false) {
    const item = document.createElement("span");
    item.className = "breadcrumb-item";

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

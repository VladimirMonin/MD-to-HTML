/**
 * Smooth Scroll for TOC - ES6 Module
 */

export function smoothScrollTOC() {
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
  console.log("✅ Smooth scroll for TOC enabled");
}

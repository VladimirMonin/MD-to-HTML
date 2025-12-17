/**
 * Main Entry Point - ES6 Modules
 * Импортирует и инициализирует все модули
 */

import { addCodeCopyButtons } from "./modules/codeCopy.js";
import { enableFullscreenMedia } from "./modules/fullscreen.js";
import { initDynamicBreadcrumbs } from "./modules/breadcrumbs.js";
import { smoothScrollTOC } from "./modules/smoothScroll.js";
import { initMermaid } from "./modules/mermaid.js";

document.addEventListener("DOMContentLoaded", function () {
  console.log("📚 Book enhancements loading...");

  try {
    addCodeCopyButtons();
    enableFullscreenMedia();
    smoothScrollTOC();
    initDynamicBreadcrumbs();
    initMermaid();

    console.log("✅ All enhancements loaded successfully");
  } catch (error) {
    console.error("❌ Error loading enhancements:", error);
  }
});

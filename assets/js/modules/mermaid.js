/**
 * Mermaid Initialization - ES6 Module
 */

export function initMermaid() {
  if (typeof mermaid !== "undefined") {
    console.log(
      "🔵 Mermaid library found, version:",
      mermaid.version || "unknown"
    );

    // Получаем конфигурацию из window.mermaidConfig (задается из Python)
    const config = window.mermaidConfig || {
      startOnLoad: false,
      theme: "neutral",
      securityLevel: "loose",
      logLevel: "debug",
    };

    // Настройка Mermaid
    mermaid.initialize(config);

    console.log(`✅ Mermaid configured (theme: ${config.theme}, securityLevel: ${config.securityLevel})`);

    // Поиск всех Mermaid блоков
    const mermaidElements = document.querySelectorAll("div.mermaid, .mermaid");
    console.log(`🔍 Found ${mermaidElements.length} Mermaid blocks to render`);

    if (mermaidElements.length > 0) {
      // Логируем содержимое каждого блока
      mermaidElements.forEach((el, index) => {
        const content = el.textContent.trim();
        console.log(`\n📊 Diagram ${index + 1}:`);
        console.log(`   Type: ${content.split("\n")[0]}`);
        console.log(`   Length: ${content.length} chars`);
        console.log(`   Preview:`, content.substring(0, 100) + "...");
      });

      // Запускаем рендеринг с обработкой ошибок
      try {
        mermaid
          .run()
          .then(() => {
            console.log("✅ All Mermaid diagrams rendered successfully");

            // Проверяем результат
            const renderedSVGs = document.querySelectorAll(
              "div.mermaid svg, .mermaid svg"
            );
            console.log(
              `✅ Rendered ${renderedSVGs.length} / ${mermaidElements.length} diagrams`
            );

            if (renderedSVGs.length < mermaidElements.length) {
              console.error(
                `❌ Some diagrams failed to render! Expected ${mermaidElements.length}, got ${renderedSVGs.length}`
              );
            }
          })
          .catch((error) => {
            console.error("❌ Mermaid rendering failed:", error);
            console.error("Error details:", error.message);
            console.error("Stack:", error.stack);
          });
      } catch (error) {
        console.error("❌ Mermaid.run() failed:", error);
      }
    } else {
      console.log("ℹ️ No Mermaid diagrams found on page");
    }
  } else {
    console.error("❌ Mermaid library not found!");
  }
}

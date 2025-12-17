/**
 * Mermaid Initialization - ES6 Module
 */

export function initMermaid() {
  if (typeof mermaid !== "undefined") {
    mermaid.initialize({
      startOnLoad: true,
      theme: "default",
      securityLevel: "loose",
    });
    console.log("✅ Mermaid initialized");
  }
}

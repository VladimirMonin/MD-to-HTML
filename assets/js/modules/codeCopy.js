/**
 * Code Copy Buttons - ES6 Module
 */

export function addCodeCopyButtons() {
  document.querySelectorAll("pre:not(.mermaid)").forEach((preBlock) => {
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

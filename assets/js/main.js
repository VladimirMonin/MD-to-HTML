document.addEventListener("DOMContentLoaded", function () {
  const elementsToCenter = {
    img: ["img-fluid", "d-block", "mx-auto"],
    iframe: ["d-block", "mx-auto"],
    table: ["table", "table-striped"],
    video: ["d-block", "mx-auto"],
  };
  centerElements(elementsToCenter);
  processBlockquotes();
  addCodeCopyButtons();
  enableFullscreenImages();
  initVideoPlayer();
});

function centerElements(elementsToCenter) {
  Object.entries(elementsToCenter).forEach(([tag, classes]) =>
    addClassesToElements(tag, classes)
  );
}

function addClassesToElements(tag, classes) {
  document.querySelectorAll(tag).forEach((el) => {
    classes.forEach((className) => el.classList.add(className));
  });
}

function processBlockquotes() {
  document.querySelectorAll("blockquote").forEach((blockquote) => {
    const firstElement = blockquote.firstElementChild;
    if (firstElement && firstElement.tagName === "P") {
      const content = firstElement.textContent.trim();
      const alertTypes = {
        "[!info]": "alert-info",
        "[!warning]": "alert-warning",
      };
      const alertClass = alertTypes[content];
      if (alertClass) {
        blockquote.classList.add("alert", alertClass);
        firstElement.classList.add("hidden-info");
      }
    }
  });
}

function addCodeCopyButtons() {
  document.querySelectorAll("pre").forEach((preBlock) => {
    preBlock.classList.add("pre-container");
    const copyButton = createCopyButton();
    preBlock.appendChild(copyButton);
    copyButton.addEventListener(
      "click",
      handleCopyButtonClick.bind(null, preBlock, copyButton)
    );
  });
}

function createCopyButton() {
  const btn = document.createElement("i");
  btn.classList.add("bi", "bi-clipboard", "code-copy-btn");
  return btn;
}

function handleCopyButtonClick(preBlock, copyButton) {
  const codeContent = preBlock.querySelector("code").innerText;
  navigator.clipboard.writeText(codeContent).then(() => {
    toggleCopyIcon(copyButton, true);
    setTimeout(() => toggleCopyIcon(copyButton, false), 3000);
  });
}

function toggleCopyIcon(copyButton, copied) {
  copyButton.classList.toggle("bi-clipboard", !copied);
  copyButton.classList.toggle("bi-clipboard-check", copied);
  copyButton.style.color = copied ? "lightgreen" : "white";
}

function enableFullscreenImages() {
  const fullscreenContainer = createFullscreenContainer();
  document.body.appendChild(fullscreenContainer);

  document.querySelectorAll("img").forEach((img) => {
    img.addEventListener("click", () =>
      showFullscreenImage(fullscreenContainer, img.src)
    );
  });

  fullscreenContainer.addEventListener("click", () => {
    fullscreenContainer.classList.remove("active");
  });
}

function createFullscreenContainer() {
  const container = document.createElement("div");
  container.classList.add("fullscreen-img-container");
  return container;
}

function showFullscreenImage(container, src) {
  container.innerHTML = `<img src="${src}" alt="Полноэкранное изображение" />`;
  container.classList.add("active");
}

function initVideoPlayer() {
  if (typeof Plyr === "undefined") {
    console.error("Plyr is not loaded correctly.");
    return;
  }

  const players = Plyr.setup("video", {
    controls: [
      "play-large",
      "play",
      "progress",
      "current-time",
      "duration",
      "mute",
      "volume",
      "fullscreen",
    ],
    settings: ["speed"],
    speed: {
      selected: 1,
      options: [0.5, 1, 1.25, 1.5, 2, 2.25, 2.5],
    },
  });

  if (!players.length) {
    console.warn("No videos were found to initialize Plyr on.");
  }
}

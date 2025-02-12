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
  const videoElements = document.querySelectorAll("video");

  if (!videoElements.length) {
    console.log("На странице нет видео элементов");
    return;
  }

  if (typeof Plyr === "undefined") {
    console.log("Plyr не загружен");
    return;
  }

  Plyr.setup("video", {
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
}

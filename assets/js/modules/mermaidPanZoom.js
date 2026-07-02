/**
 * Lightweight local Mermaid SVG pan/zoom module.
 * No CDN/runtime dependency: works with inline SVG generated in copy-mode.
 */

const _mermaidPanZoomInstances = new WeakMap();

function ensureTransformLayer(svg) {
  let layer = svg.querySelector("g.mermaid-panzoom-layer");
  if (layer) return layer;

  layer = document.createElementNS("http://www.w3.org/2000/svg", "g");
  layer.classList.add("mermaid-panzoom-layer");
  while (svg.firstChild) layer.appendChild(svg.firstChild);
  svg.appendChild(layer);
  return layer;
}

function createController(shell) {
  const viewport = shell.querySelector(".mermaid-viewport");
  const svg = viewport ? viewport.querySelector("svg") : null;
  if (!viewport || !svg) return null;

  // Mermaid CLI writes intrinsic sizing into the inline SVG style, including
  // `max-width: <diagram width>px`. For tall diagrams that cap can leave the
  // actual SVG as a narrow strip at the left side of a wide viewport. Normalize
  // the root SVG sizing before transforms so `preserveAspectRatio` can center
  // portrait and wide diagrams inside the viewport in normal and fullscreen modes.
  svg.setAttribute("preserveAspectRatio", "xMidYMid meet");
  svg.style.width = "100%";
  svg.style.height = "100%";
  svg.style.maxWidth = "none";
  svg.style.display = "block";

  const layer = ensureTransformLayer(svg);
  let scale = 1;
  let x = 0;
  let y = 0;
  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  const apply = () => {
    layer.setAttribute("transform", `translate(${x} ${y}) scale(${scale})`);
  };

  const zoom = (factor, centerX, centerY) => {
    const nextScale = Math.min(8, Math.max(0.25, scale * factor));
    if (nextScale === scale) return;
    const rect = viewport.getBoundingClientRect();
    const cx = centerX ?? rect.left + rect.width / 2;
    const cy = centerY ?? rect.top + rect.height / 2;
    const localX = cx - rect.left - rect.width / 2;
    const localY = cy - rect.top - rect.height / 2;
    const ratio = nextScale / scale;
    x = localX - (localX - x) * ratio;
    y = localY - (localY - y) * ratio;
    scale = nextScale;
    apply();
  };

  const reset = () => {
    scale = 1;
    x = 0;
    y = 0;
    apply();
  };

  viewport.addEventListener("wheel", (event) => {
    event.preventDefault();
    zoom(event.deltaY < 0 ? 1.15 : 1 / 1.15, event.clientX, event.clientY);
  }, { passive: false });

  viewport.addEventListener("pointerdown", (event) => {
    dragging = true;
    lastX = event.clientX;
    lastY = event.clientY;
    viewport.setPointerCapture(event.pointerId);
    viewport.classList.add("is-dragging");
  });

  viewport.addEventListener("pointermove", (event) => {
    if (!dragging) return;
    x += event.clientX - lastX;
    y += event.clientY - lastY;
    lastX = event.clientX;
    lastY = event.clientY;
    apply();
  });

  const stopDragging = () => {
    dragging = false;
    viewport.classList.remove("is-dragging");
  };
  viewport.addEventListener("pointerup", stopDragging);
  viewport.addEventListener("pointercancel", stopDragging);
  viewport.addEventListener("dblclick", (event) => zoom(1.35, event.clientX, event.clientY));

  shell.querySelector(".mermaid-zoom-in")?.addEventListener("click", () => zoom(1.25));
  shell.querySelector(".mermaid-zoom-out")?.addEventListener("click", () => zoom(1 / 1.25));
  shell.querySelector(".mermaid-reset")?.addEventListener("click", reset);
  shell.querySelector(".mermaid-panzoom-fullscreen")?.addEventListener("click", async () => {
    if (document.fullscreenElement === shell) {
      await document.exitFullscreen();
    } else if (shell.requestFullscreen) {
      await shell.requestFullscreen();
    } else {
      shell.classList.toggle("is-fullscreen-fallback");
    }
    setTimeout(reset, 50);
  });

  apply();
  return { reset, zoom };
}

export function initMermaidPanZoom() {
  document.querySelectorAll(".mermaid-panzoom-shell").forEach((shell) => {
    if (_mermaidPanZoomInstances.has(shell)) return;
    const controller = createController(shell);
    if (controller) _mermaidPanZoomInstances.set(shell, controller);
  });
}

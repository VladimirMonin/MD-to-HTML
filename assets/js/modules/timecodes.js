/* Static timecode panels for nearby audio/video media. */

function initTimecodes() {
  const panels = Array.from(document.querySelectorAll('[data-timecodes]'));
  if (!panels.length) return;

  tagMediaElements();

  panels.forEach((panel) => {
    const media = findAssociatedMedia(panel);
    if (!media) {
      panel.classList.add('timecode-panel--no-media');
      return;
    }

    panel.__mdToHtmlMedia = media;
    panel.setAttribute('data-media-target', media.getAttribute('data-md-media-id'));

    panel.querySelectorAll('[data-seek-seconds]').forEach((button) => {
      button.addEventListener('click', () => {
        const seconds = Number(button.getAttribute('data-seek-seconds'));
        if (!Number.isFinite(seconds)) return;
        seekMedia(media, seconds);
        setActiveTimecode(panel, button);
      });
    });
  });
}

function initTimecodeSeek() {
  return initTimecodes();
}

function tagMediaElements() {
  document.querySelectorAll('audio, video').forEach((media, index) => {
    const existingId = media.getAttribute('id');
    const mediaId = existingId || `md-media-${index + 1}`;

    if (!existingId) {
      media.setAttribute('id', mediaId);
    }

    if (!media.hasAttribute('data-md-media-id')) {
      media.setAttribute('data-md-media-id', mediaId);
    }
  });
}

function findAssociatedMedia(panel) {
  const media = Array.from(document.querySelectorAll('audio, video')).filter(
    (element) => !panel.contains(element),
  );
  if (!media.length) return null;

  const panelPosition = getDocumentPosition(panel);
  const ranked = media.map((element, index) => ({
    element,
    index,
    position: getDocumentPosition(element),
  }));

  const previous = ranked
    .filter((item) => item.position < panelPosition)
    .sort((a, b) => b.position - a.position);
  if (previous.length) return previous[0].element;

  return ranked.sort((a, b) => a.position - b.position || a.index - b.index)[0].element;
}

function getDocumentPosition(element) {
  const walker = document.createTreeWalker(document.body || document.documentElement, NodeFilter.SHOW_ELEMENT);
  let index = 0;
  let node = walker.currentNode;
  while (node) {
    if (node === element) return index;
    index += 1;
    node = walker.nextNode();
  }
  return Number.MAX_SAFE_INTEGER;
}

function seekMedia(media, seconds) {
  media.currentTime = seconds;

  const player = media.__mdToHtmlPlyr || media.plyr;
  if (player && typeof player === 'object') {
    try {
      player.currentTime = seconds;
    } catch (error) {
      // Native currentTime above is the source of truth; Plyr may reject before metadata is loaded.
    }
  }

  media.dispatchEvent(new Event('timeupdate', { bubbles: true }));
  media.dispatchEvent(new Event('seeked', { bubbles: true }));
  syncPlyrVisibleState(media, seconds);
}

function syncPlyrVisibleState(media, seconds) {
  const container = getMediaUiContainer(media);
  if (!container) return;

  const currentTime = container.querySelector('.plyr__time--current');
  if (currentTime) currentTime.textContent = formatTimecode(seconds);

  const duration = Number.isFinite(media.duration) && media.duration > 0 ? media.duration : null;
  const seekValue = duration ? Math.max(0, Math.min(100, (seconds / duration) * 100)) : seconds;

  container.querySelectorAll('input[type="range"]').forEach((input) => {
    const isSeek = input.getAttribute('data-plyr') === 'seek' || input.classList.contains('plyr__progress__input') || input.closest('.plyr__progress');
    if (!isSeek) return;
    const value = String(Math.round(seekValue * 1000) / 1000);
    input.value = value;
    input.setAttribute('aria-valuenow', value);
    input.setAttribute('aria-valuetext', formatTimecode(seconds));
    input.style.setProperty('--value', `${value}%`);
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  });
}

function getMediaUiContainer(media) {
  const figure = media.closest('figure, .media-player');
  const nativePlyr = media.closest('.plyr');
  if (nativePlyr) return nativePlyr;

  const mediaId = media.getAttribute('data-md-media-id');
  if (figure) {
    const nestedPlyr = figure.querySelector('.plyr');
    if (nestedPlyr) return nestedPlyr;
  }

  if (mediaId) {
    const siblingPlyr = document.querySelector(`.plyr [data-md-media-id="${mediaId}"]`);
    if (siblingPlyr) return siblingPlyr.closest('.plyr');
  }

  return figure || media.parentElement;
}

function setActiveTimecode(panel, activeButton) {
  panel.querySelectorAll('[data-seek-seconds]').forEach((button) => {
    const isActive = button === activeButton;
    button.classList.toggle('is-active', isActive);
    button.setAttribute('aria-current', isActive ? 'true' : 'false');
  });
}

function formatTimecode(totalSeconds) {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const hours = Math.floor(safeSeconds / 3600);
  const minutes = Math.floor((safeSeconds % 3600) / 60);
  const seconds = safeSeconds % 60;
  const mm = String(minutes).padStart(2, '0');
  const ss = String(seconds).padStart(2, '0');
  if (hours > 0) return `${hours}:${mm}:${ss}`;
  return `${mm}:${ss}`;
}

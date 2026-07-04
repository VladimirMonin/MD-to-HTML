"""Tests for static media timecode panels."""

from __future__ import annotations

import json
import shutil
import socket
import subprocess
import textwrap
import time
import urllib.request
from pathlib import Path

import pytest

from md_converter import Converter, ConverterConfig
from md_converter.preprocessors.timecodes import TimecodesPreprocessor
from md_converter.processors.template import TemplateProcessor
from md_converter.config import FeaturesConfig, StylesConfig


ROOT = Path(__file__).resolve().parents[1]


def test_timecodes_preprocessor_escapes_labels_and_renders_buttons():
    source = """# Demo

```timecodes
00:12 Intro <script>alert(1)</script>
1:02:03 Deep dive
```
"""

    html = TimecodesPreprocessor().process(source)

    assert '<section class="timecode-panel" data-timecodes' in html
    assert 'data-seek-seconds="12"' in html
    assert 'data-seek-seconds="3723"' in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<script>alert(1)</script>' not in html


def test_template_includes_timecode_assets_and_initializes_after_plyr():
    header = TemplateProcessor(
        template="web",
        features=FeaturesConfig(),
        styles=StylesConfig(),
        media_mode="embed",
    ).build_header("html")

    assert "assets/css/modules/timecodes.css" in header
    assert "Static timecode panels" in header
    assert "function initTimecodes()" in header
    assert "function initTimecodeSeek()" in header
    assert header.index("Plyr.setup") < header.index("if (typeof initTimecodes")


def test_timecode_css_attaches_to_adjacent_media_without_overlap():
    css = (ROOT / "assets" / "css" / "modules" / "timecodes.css").read_text(encoding="utf-8")
    media_css = (ROOT / "assets" / "css" / "modules" / "media.css").read_text(encoding="utf-8")

    assert "figure.media-player + .timecode-panel" in css
    assert ".plyr + .timecode-panel" in css
    assert "margin-top: -" not in css
    assert "border-radius: 0 0 16px 16px" in css
    assert "text-transform: uppercase" not in css
    assert "background: #334155" not in css
    assert "figure.media-player:has(+ .timecode-panel)" in media_css
    assert ".plyr:has(+ .timecode-panel)" in media_css
    assert "margin-bottom: 0" in media_css


def test_converter_outputs_timecode_panel(tmp_path):
    note = tmp_path / "note.md"
    note.write_text(
        """# Demo

```timecodes
00:03 Start
```
""",
        encoding="utf-8",
    )

    config = ConverterConfig()
    config.formats = ["html"]
    config.media_mode = "copy"
    config.output_dir = str(tmp_path / "build")
    config.features.mermaid = False
    config.features.toc = False
    config.metadata.title = "Timecodes"

    output = Converter(config).convert(note, "timecodes")[0]
    html = output.read_text(encoding="utf-8")

    assert '<section class="timecode-panel" data-timecodes' in html
    assert 'data-seek-seconds="3"' in html
    assert (tmp_path / "build" / "assets" / "js" / "modules" / "timecodes.js").exists()
    assert (tmp_path / "build" / "assets" / "css" / "modules" / "timecodes.css").exists()


def test_timecode_browser_targets_video_after_plyr_like_wrapping(tmp_path):
    chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    node = shutil.which("node")
    if not chrome or not node:
        pytest.skip("Chrome and Node are required for the browser DOM timecode regression")

    js_code = (ROOT / "assets" / "js" / "modules" / "timecodes.js").read_text(encoding="utf-8")
    html = tmp_path / "fixture.html"
    html.write_text(
        f"""<!doctype html>
<html><body>
<figure class="media-player media-audio">
  <div class="plyr plyr--audio">
    <audio style="height:0;width:0"></audio>
    <span class="plyr__time--current">00:00</span>
    <div class="plyr__progress"><input type="range" data-plyr="seek" value="0" aria-valuenow="0" style="--value: 0%"></div>
  </div>
</figure>
<figure class="media-player media-video">
  <div class="plyr plyr--video">
    <video style="height:0;width:0"></video>
    <span class="plyr__time--current">00:00</span>
    <div class="plyr__progress"><input type="range" data-plyr="seek" value="0" aria-valuenow="0" style="--value: 0%"></div>
  </div>
</figure>
<section class="timecode-panel" data-timecodes>
  <button type="button" class="timecode-button" data-seek-seconds="180" aria-current="false">03:00 Video mark</button>
</section>
<script>{js_code}</script>
<script>
initTimecodeSeek();
Object.defineProperty(document.getElementById('md-media-1'), 'duration', {{ value: 300, configurable: true }});
Object.defineProperty(document.getElementById('md-media-2'), 'duration', {{ value: 300, configurable: true }});
</script>
</body></html>""",
        encoding="utf-8",
    )

    port = _free_port()
    user_data = tmp_path / "chrome-profile"
    proc = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--no-first-run",
            "--disable-gpu",
            "--no-sandbox",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data}",
            html.as_uri(),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        ws_url = _wait_for_cdp(port, html.as_uri())
        result = _evaluate_with_node(
            ws_url,
            """
(async () => {
  for (let i = 0; i < 50 && !document.querySelector('.timecode-button'); i += 1) {
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  const audio = document.getElementById('md-media-1');
  const video = document.getElementById('md-media-2');
  const button = document.querySelector('.timecode-button');
  button.click();
  const videoSeek = document.querySelector('.media-video input[data-plyr="seek"]');
  const audioSeek = document.querySelector('.media-audio input[data-plyr="seek"]');
  return {
    panelTarget: document.querySelector('[data-timecodes]').getAttribute('data-media-target'),
    mediaIds: Array.from(document.querySelectorAll('[id^="md-media-"]')).map((item) => item.id),
    audioTime: audio.currentTime,
    videoTime: video.currentTime,
    videoCurrentText: document.querySelector('.media-video .plyr__time--current').textContent,
    videoSeekValue: videoSeek.value,
    videoSeekAria: videoSeek.getAttribute('aria-valuenow'),
    videoSeekStyle: videoSeek.style.getPropertyValue('--value'),
    audioSeekValue: audioSeek.value,
    active: button.classList.contains('is-active'),
    ariaCurrent: button.getAttribute('aria-current')
  };
})()
""",
        )
    finally:
        proc.terminate()
        proc.wait(timeout=10)

    assert result["panelTarget"] == "md-media-2"
    assert result["mediaIds"] == ["md-media-1", "md-media-2"]
    assert result["audioTime"] == 0
    assert result["videoTime"] == 180
    assert result["videoCurrentText"] == "03:00"
    assert result["videoSeekValue"] == "60"
    assert result["videoSeekAria"] == "60"
    assert result["videoSeekStyle"] == "60%"
    assert result["audioSeekValue"] == "0"
    assert result["active"] is True
    assert result["ariaCurrent"] == "true"


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_cdp(port: int, expected_url: str) -> str:
    url = f"http://127.0.0.1:{port}/json/list"
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                pages = json.loads(response.read().decode("utf-8"))
            for page in pages:
                if page.get("type") == "page" and page.get("url") == expected_url:
                    return page["webSocketDebuggerUrl"]
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("Chrome DevTools endpoint did not become ready")


def _evaluate_with_node(ws_url: str, expression: str) -> dict:
    node_script = textwrap.dedent(
        """
        const wsUrl = process.argv[1];
        const expression = process.argv[2];
        const ws = new WebSocket(wsUrl);
        let nextId = 1;
        const pending = new Map();

        function send(method, params = {}) {
          const id = nextId++;
          ws.send(JSON.stringify({ id, method, params }));
          return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
        }

        ws.onmessage = (event) => {
          const message = JSON.parse(event.data);
          if (!message.id || !pending.has(message.id)) return;
          const { resolve, reject } = pending.get(message.id);
          pending.delete(message.id);
          if (message.error) reject(new Error(JSON.stringify(message.error)));
          else resolve(message.result);
        };

        ws.onopen = async () => {
          try {
            await send('Runtime.enable');
            const result = await send('Runtime.evaluate', {
              expression,
              awaitPromise: true,
              returnByValue: true,
            });
            if (result.exceptionDetails) {
              throw new Error(JSON.stringify(result.exceptionDetails));
            }
            console.log(JSON.stringify(result.result.value));
            ws.close();
          } catch (error) {
            console.error(error.stack || error.message);
            process.exitCode = 1;
            ws.close();
          }
        };

        ws.onerror = (error) => {
          console.error(error.message || String(error));
          process.exitCode = 1;
        };
        """
    )
    completed = subprocess.run(
        ["node", "-e", node_script, ws_url, expression],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return json.loads(completed.stdout)

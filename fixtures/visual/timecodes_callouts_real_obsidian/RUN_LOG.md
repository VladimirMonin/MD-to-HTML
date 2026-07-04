# Real Obsidian visual fixture run log

Kanban task: `t_f37b695d`

## Commands run

From repo root `/home/v/code/MD-to-HTML/.worktrees/t_fixture_audit`:

```bash
# Build/refresh source pack and generated local test media.
PACK='fixtures/visual/timecodes_callouts_real_obsidian'
rm -rf "$PACK" build/visual-fixtures/timecodes-callouts-real-obsidian
mkdir -p "$PACK/source" "$PACK/source/raw-html-parity" "$PACK/run" "$PACK/audit"
SRC='/home/v/Syncthing/AUTO_OBSIDIAN/999_files/lm-studio'
cp "$SRC/cover-01.webp" "$PACK/source/cover-01.webp"
cp "$SRC/01-1.webp" "$PACK/source/lm-studio-01-1.webp"
AUDIO=$(find "$SRC" -maxdepth 1 -type f -name '01_*.opus' | sort | head -n 1)
cp "$AUDIO" "$PACK/source/lm-studio-01-audio.opus"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc2=size=640x360:rate=24 -f lavfi -i sine=frequency=660:sample_rate=44100 -t 8 -pix_fmt yuv420p -c:v libx264 -preset ultrafast -c:a aac -shortest "$PACK/source/local-demo-video.mp4"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i sine=frequency=440:sample_rate=44100 -t 8 -c:a pcm_s16le "$PACK/source/raw-html-parity/raw-local-tone.wav"
ffmpeg -hide_banner -loglevel error -y -f lavfi -i testsrc=size=320x180:rate=24 -t 8 -pix_fmt yuv420p -c:v libx264 -preset ultrafast "$PACK/source/raw-html-parity/raw-local-video.mp4"

# Fresh render to removed output directories.
rm -rf build/visual-fixtures/timecodes-callouts-real-obsidian/copy build/visual-fixtures/timecodes-callouts-real-obsidian/embed
uv run python cli.py fixtures/visual/timecodes_callouts_real_obsidian/source/real_obsidian_visual_fixture.md -c fixtures/visual/timecodes_callouts_real_obsidian/run/config.copy.yaml -o real_obsidian_visual_fixture -f html -m copy -t web
uv run python cli.py fixtures/visual/timecodes_callouts_real_obsidian/source/real_obsidian_visual_fixture.md -c fixtures/visual/timecodes_callouts_real_obsidian/run/config.embed.yaml -o real_obsidian_visual_fixture -f html -m embed -t web

# Pre-manual-copy audit: expected failure for isolated raw HTML parity media only.
python fixtures/visual/timecodes_callouts_real_obsidian/audit/audit_html_artifacts.py \
  build/visual-fixtures/timecodes-callouts-real-obsidian/copy/real_obsidian_visual_fixture.html \
  build/visual-fixtures/timecodes-callouts-real-obsidian/embed/real_obsidian_visual_fixture.html \
  --json-out fixtures/visual/timecodes_callouts_real_obsidian/audit/pre_manual_copy_audit.json

# Manual copy for the explicit raw HTML parity/negative case.
for mode in copy embed; do
  mkdir -p "build/visual-fixtures/timecodes-callouts-real-obsidian/$mode/raw-html-parity"
  cp fixtures/visual/timecodes_callouts_real_obsidian/source/raw-html-parity/raw-local-tone.wav "build/visual-fixtures/timecodes-callouts-real-obsidian/$mode/raw-html-parity/raw-local-tone.wav"
  cp fixtures/visual/timecodes_callouts_real_obsidian/source/raw-html-parity/raw-local-video.mp4 "build/visual-fixtures/timecodes-callouts-real-obsidian/$mode/raw-html-parity/raw-local-video.mp4"
done

# Final artifact audit.
python fixtures/visual/timecodes_callouts_real_obsidian/audit/audit_html_artifacts.py \
  build/visual-fixtures/timecodes-callouts-real-obsidian/copy/real_obsidian_visual_fixture.html \
  build/visual-fixtures/timecodes-callouts-real-obsidian/embed/real_obsidian_visual_fixture.html \
  --json-out fixtures/visual/timecodes_callouts_real_obsidian/audit/post_manual_copy_audit.json
```

## Output folders

- Copy render: `build/visual-fixtures/timecodes-callouts-real-obsidian/copy/real_obsidian_visual_fixture.html`
- Embed render: `build/visual-fixtures/timecodes-callouts-real-obsidian/embed/real_obsidian_visual_fixture.html`

Generated output directories were removed before rendering.

## Manifest

- `fixtures/visual/timecodes_callouts_real_obsidian/MANIFEST.md`

## Artifact audit evidence

Pre-manual-copy audit:

```json
{"total": 46, "data": 5, "external": 4, "local": 23, "local_missing": 4}
```

The 4 missing local files were exactly the isolated raw HTML parity/negative case:

- copy/raw-html-parity/raw-local-tone.wav
- copy/raw-html-parity/raw-local-video.mp4
- embed/raw-html-parity/raw-local-tone.wav
- embed/raw-html-parity/raw-local-video.mp4

Post-manual-copy audit:

```json
{"total": 46, "data": 5, "external": 4, "local": 23, "local_missing": 0}
```

Detailed reports:

- `fixtures/visual/timecodes_callouts_real_obsidian/audit/pre_manual_copy_audit.json`
- `fixtures/visual/timecodes_callouts_real_obsidian/audit/post_manual_copy_audit.json`

## Manual-copy status

Manual copy was needed only for the explicit raw HTML parity/negative case. The primary Obsidian image/audio/video embeds were packaged by the converter path.

## Render observations

Current rendered HTML contains, in both copy and embed modes:

- 2 `<audio>` elements: one primary Obsidian audio embed and one raw HTML parity audio element.
- 2 `<video>` elements: one primary Obsidian video embed and one raw HTML parity video element.
- 3 `<img>` elements: cover, screenshot, Mermaid diagram.
- Obsidian callouts are present as Pandoc fenced-div classes (`note`, `warning`, `question`, `important`), not yet as the desired future `.callout ... data-callout` DOM contract.
- `timecodes` fences are preserved as literal code blocks in this baseline; the timecode implementation is expected in a downstream fix card.

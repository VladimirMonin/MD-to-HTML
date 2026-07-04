# Real Obsidian visual fixture manifest

Kanban task: `t_f37b695d`

Source pack root: `fixtures/visual/timecodes_callouts_real_obsidian/`

## Fixture document

| Pack path | Origin | Notes |
|---|---|---|
| `source/real_obsidian_visual_fixture.md` | Generated local test note for this task | Uses Obsidian embeds `![[...]]` for the primary image/audio/video path; includes isolated raw HTML parity/negative case. |

## Media files

| Pack path | Origin | Notes |
|---|---|---|
| `source/cover-01.webp` | `/home/v/Syncthing/AUTO_OBSIDIAN/999_files/lm-studio/cover-01.webp` | Real Obsidian vault image asset. |
| `source/lm-studio-01-1.webp` | `/home/v/Syncthing/AUTO_OBSIDIAN/999_files/lm-studio/01-1.webp` | Real Obsidian vault screenshot asset. |
| `source/lm-studio-01-audio.opus` | `/home/v/Syncthing/AUTO_OBSIDIAN/999_files/lm-studio/01_*.opus` | Real Obsidian vault audio asset; copied via glob to avoid shelling a Cyrillic filename into scripts. |
| `source/local-demo-video.mp4` | Generated locally with `ffmpeg` testsrc2 + sine | Generated because no real `.mp4` was found in the vault during this task. Used through Obsidian embed syntax. |
| `source/raw-html-parity/raw-local-tone.wav` | Generated locally with `ffmpeg` sine | Raw HTML parity/negative case only; not the primary Obsidian path. |
| `source/raw-html-parity/raw-local-video.mp4` | Generated locally with `ffmpeg` testsrc | Raw HTML parity/negative case only; not the primary Obsidian path. |

## Render configs

| Pack path | Purpose |
|---|---|
| `run/config.copy.yaml` | Copy-mode render into `build/visual-fixtures/timecodes-callouts-real-obsidian/copy`. |
| `run/config.embed.yaml` | Embed-mode render into `build/visual-fixtures/timecodes-callouts-real-obsidian/embed`. |
| `audit/audit_html_artifacts.py` | Lists every HTML `src`/`href`, classifies data/external/local references, and fails if any local reference is missing relative to the HTML file. |

## Manual-copy policy

Expected clean converter behavior: primary Obsidian image/audio/video embeds are packaged by the converter.

Known explicit parity/negative case: raw HTML audio/video paths are not Markdown media links. This fixture keeps them isolated under `raw-html-parity/`; if a render needs those raw files copied beside HTML for browser parity, the command log must call that manual copy out explicitly.

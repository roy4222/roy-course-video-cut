# lemo-opuscar dependency (third-party, NOT vendored)

- Upstream: https://github.com/lemomo-ai/lemo-opuscar (MIT)
- Commit used on the box: `f17136060781a0068a7951245a3aa7835a7230de`
  (2026-10-29 16:50:59 +1100 = 2026-10-29 13:50 Asia/Taipei, "Merge #10 from waiting761: Chinese numerals in asr_check")
- Box checkout: `/workspace/video_style/lemo-opuscar` (node deps: playwright-core ^1.63.0 → 1.63.0 installed, three ^0.170.0;
  browser: playwright chromium_headless_shell-1243; its own `.venv` is used only to run `core/render/srt.py`).

## Parts our pipelines call (box pipelines A/B/C/D)
| upstream file | used by | how |
|---|---|---|
| `core/render/page.mjs` (+ `serve.mjs`, `browser.mjs`) | `layout.mjs` (B/D), video/still | `openDemo(dir)` serves a film dir over HTTP and opens it in headless Chromium |
| `core/render/video.mjs` | all box pipelines | `node core/render/video.mjs <filmdir> --fps 30 --workers N --out <ep>/out/video.mp4` (parallel Chromium workers → JPEG → ffmpeg image2pipe → lossless concat). Env `RENDER_SLOTS` optional. |
| `core/render/still.mjs` | `stills.py` (B/D), `make_ep.py stills` (A/C) | end-of-scene preview frames |
| `core/render/mux.sh` | A/C `stage_mux`, B/D `mix()` | `sh core/render/mux.sh video.mp4 mix_lim.wav epNN.mp4 30 0` → two-pass loudnorm I=-14 TP=-1.2 LRA=11, libx264 preset slow crf 19, AAC 256k, prints ebur128 I/Peak |
| `core/render/srt.py` | all | `python core/render/srt.py cues.json epNN.srt` |
| `core/tts/tts_zh.py` | fallback only (VOICE.md) | edge-tts zh-TW-HsiaoChenNeural |
| `films/` | A/C only | `make_ep.py` symlinks `films/epNN → <ep>/film` and renders `films/epNN` |

## Our additions inside the checkout (copied here, not upstream)
`git status` in the checkout shows these as untracked / modified — they are OUR code and live in `engine/lemo_overlay/`:
- `core/tts/tts_openrouter.py` — OpenRouter TTS (Gemini 3.8 Flash TTS, Enceladus), `--mode scene|line`, whisper alignment via `or_align.py`
- `core/tts/or_align.py` — faster-whisper word-timestamp alignment of scene audio to lines (`split_scene`)
- `core/tts/or_silence.py` — ASR-free pause-based split (DP)
- `core-README.md.patch` — 7-line addition to upstream `core/README.md` documenting the project voice default

To reproduce: `git clone https://github.com/lemomo-ai/lemo-opuscar && git -C lemo-opuscar checkout f171360 && cp -r engine/lemo_overlay/core/tts/*.py lemo-opuscar/core/tts/ && npm --prefix lemo-opuscar ci`.

The Windows kit (`windows-kit/render/*.mjs`) contains small **modified copies** of `serve/browser/page/still/video.mjs`
(serve.mjs identical; others differ by 4–16 diff lines, e.g. `KIT_VCODEC=nvenc` segment encoding) with the MIT license in
`windows-kit/licenses/lemo-opuscar-MIT.txt`. That is the only upstream-derived code in this bundle.

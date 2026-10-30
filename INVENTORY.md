# INVENTORY — 「機器學習從零開始」video production pipeline (source bundle, 2026-10-30)

> **Repo layout note (2026-10-30):** this inventory was written before the tree was organized for the public repository.
> The `engine/` directory described below now lives at `legacy/` (historical pipelines A–D, QC, and the lemo overlay). New episodes use `windows-kit/`.
> Private YouTube video IDs are placeholders (`REDACTED-…`) because the GitHub repository is public. One machine-specific directory name in the source list below was redacted to `<kit-build>`.
>
> **版面說明：** 現在做片請用 `windows-kit/`。`legacy/` 是舊管線，只留著對照。給維護者的說明在根目錄 `README.md`。
>

Factual description of what is in this bundle, written from reading the code and logs on the box
(`/workspace/video_style`, `/workspace/yt_upload`, `/workspace/<kit-build>/ml-video-kit`, `/workspace/desk_xfer`)
and a read-only listing of the Windows desktop kit `D:\ml-video-kit`. All times are Asia/Taipei.
No renders (mp4/wav/png/jpg), venvs, node_modules, caches or `.env` are included.

## 0. Series & who made what
24 videos: EP00–EP20, 實戰 A1, A2 上 (A2_1), A2 下 (A2_2). Five generations of tooling were used **in parallel** today;
they share one design (script lines → TTS per scene → split per line → timeline → canvas page → Chromium frames → ffmpeg):

| tooling | where | episodes it built | episode source format |
|---|---|---|---|
| prototype (ad-hoc scripts) | box | EP01 | `episodes/ep01/script.py` + helper scripts |
| **pipeline A** `engine/pipeline_A` | box | EP00, EP02–EP05 | `src.py` with `META` + `SCENES` |
| **pipeline C** `engine/pipeline_C` | box | EP06–EP10 | `src.py` (same as A) |
| **pipeline B** `engine/pipeline_B` | box | EP11, EP13, EP15 (+ first drafts of EP12/14/16/17) | `build.py` using `lib.Ep` DSL |
| **pipeline D** `engine/pipeline_D` | box | EP18, EP20 | `build.py` using `lib.Ep` DSL |
| **windows-kit** (`ml-video-kit`) | Boss's desktop `D:\ml-video-kit` (RTX 3060 Ti, NVENC) | EP12, EP14, EP16, EP17, EP19, A1, A2_1, A2_2 | `build.py` (same DSL; `from lib import Ep` via kit PYTHONPATH) |

(Source: `notes/state/progress_*.json` "machine" fields + `progress_A12.json`.) The windows-kit `make_episode.py` is the
most complete/consolidated version (it merges pipeline D's steps + B/D engine.js) and is the recommended base for the repo.
EP00–EP10 (`src.py` format, `pipeline_A/engine.js`) are **not** supported by the kit (kit README §5 says so).

## 1. End-to-end flow (kit names; box pipelines are equivalent)
1. **Write** `episodes/<ep>/build.py` (DSL: `ep=Ep(num,title,head,summary,tags,next,accent)`, `ep.scene(id,title,...)`,
   `i=ep.L(text, say=?, gap=?)`, `ep.E(type, ..., at=i)`, `ep.save('.')`) → `script.json`, `lines.json`, `scenes.json`, `meta.json`.
   `lib.py.save` asserts every element's `at/until/qi/ai/hot/oat` index is a valid line index in its scene.
2. **tts**: lines grouped per scene into chunks ≤380 chars → one OpenRouter request per chunk
   (`POST https://openrouter.ai/api/v1/audio/speech`, model `google/gemini-3.8-flash-tts`, voice `Enceladus`, `response_format: pcm`,
   Taiwan-Mandarin teacher `instructions`) → ffmpeg s16le→24 kHz wav → split back into per-line wavs:
   (a) pause DP split `sil_split.py` (no ASR); (b) if low confidence, faster-whisper word timestamps (`whisper_align.py` / `my_align.py`);
   (c) regenerate once; (d) fall back to per-line synthesis. Cost per request read from `/api/v1/generation?id=<X-Generation-Id>` → `voice/costs.json`. `voice/dur.json` = per-line durations.
3. **timeline**: t starts 1.2 s; +0.7 s after each line (+`gap`), +1.2 s at scene change (override via `pace.json` `{"line":..,"scene":..}`); DUR = last t1 + 2.5 s.
   Writes `film/timeline.js` (`window.LINES/SCENES/EPMETA/DUR`), copies `engine.js` → `film/main.js`, `film/index.html` (1920×1080 canvas), `cues.json`.
4. **layout** (QC, warnings only): `layout.mjs` opens the page and, at each line's t0+0.9 and t1−0.05, calls `window.TEXTS(t)` to flag
   OUT-OF-FRAME (x<20, x>1900, y>1075), OVERLAP (>15 % of smaller box), UNDER-SUBTITLE → `qc/layout.txt`.
5. **render**: `video.mjs <film> --fps 30 --workers N --out out/video.mp4` — N headless Chromium workers, JPEG screenshots piped to ffmpeg, segments concatenated losslessly. Subtitles are drawn by engine.js on the canvas (= burned in).
6. **mix**: each `voice/<id>.wav` placed at its t0 on a 24 kHz buffer → `out/mix.wav` → `alimiter=limit=0.5:attack=5:release=50:level=disabled` → `out/mix_lim.wav`.
7. **mux**: two-pass `loudnorm=I=-14:TP=-1.2:LRA=11` (measured values, linear=true), `fps=30,format=yuv420p`, libx264 `-preset slow -crf 19` (or NVENC `-preset p6 -tune hq -rc vbr -cq 20`), AAC 256k, faststart → `epNN.mp4`; warns if I outside −15…−13 or TP > −1.
8. **master**: `volume=0.35dB,aresample=96000,alimiter=limit=0.8:attack=2:release=50:level=disabled,aresample=48000`, AAC 192k, `-c:v copy`; ebur128 → `qc/loudness.json`. Final measured values today: −13.7…−14.1 LUFS, TP −1.2…−1.6 dBFS.
9. **srt** → `epNN.srt` (from cues; overlapping cues clipped). **md** → `script.md` with `[mm:ss]` per line.
10. **qc**: 8 frames at 3/15/28/40/52/64/77/90 % → `qc/f*.jpg`; Whisper `small` transcribes 3 lines (20/50/80 %) with ±1 s padding → text similarity + start offset → `qc/sync.json`; ffprobe. Box `engine/qc/final_qc.py <ep>` additionally checks 1080p/30 fps, LUFS/TP, duration vs last cue, and RMS speech onsets vs 6 SRT cue starts.
11. **yt**: `youtube.json` (title `機器學習從零開始 EPNN｜<title>`, description = summary + 章節 chapter list (scene starts −0.9 s, ≥10 s apart) + series blurb, tags, `synthetic`, `language: zh-TW`, category Education). Kit/D asserts no local paths / long tokens / `sk-or-` leak into it.
12. **Upload** (Boss's MacBook only, see §6) — private visibility; playlist edited by hand in YouTube Studio (API scope is upload-only).

## 2. Entry points & exact commands used today
### windows-kit (desktop) — `windows-kit/`
- Setup: `setup.cmd [-Cuda] [-NoModels]` → `setup.ps1` (Windows) / `setup.sh [--cuda]` (Linux/macOS): uv venv, `requirements.txt` (+`requirements-cuda.txt`), `npm ci` (playwright-core 1.63.0) + chromium-headless-shell into `.browsers/`, Whisper model pre-download into `.cache/`, creates `.env` from `.env.example`.
- One episode: `make_episode.cmd <episode_dir> [steps...] [--workers N] [--nvenc] [--whisper-device cpu|cuda|auto] [--tts-mode scene|line] [--force] [--low-priority]`
  (`make_episode.sh` on Linux/macOS; both call `.venv/.../python make_episode.py`). Steps: `build tts timeline layout render mix mux master srt md qc yt` (+ extra `stills`). Finished steps are skipped by mtime/dependency stamps; re-running resumes.
- What was actually run (`run_ep.cmd <ep>`, recreated here from the desktop copy):
  `make_episode.cmd episodes\%1 tts timeline layout render mix mux master srt md qc yt --nvenc --whisper-device cuda` → `episodes\<ep>.run.log`, ending `EXIT <code>`.
- `run_ep17_tts.cmd`: `make_episode.cmd episodes\ep17 tts --tts-mode line --whisper-device cuda` (EP17 needed per-line TTS).
- `queue1.ps1 <eps...>` (wait for ep14.run.log EXIT then run each), `queue2.ps1 <wait_ep> <eps...>`, `queue3.ps1` (wait ep16 + ep17 TTS, then ep17) — **serialize renders** on the desktop because of the NVENC session limit.
- Default workers = `min(8, cpu_threads/4, RAM_GB/6)` (desktop i7-13700F/48 GB → 6; logs show `workers=6 codec=h264_nvenc`).
- `episodes/sample` (tiny smoke test; its wavs were removed from this bundle) and `episodes/ep13-example`.
### box pipeline A / C
- `/workspace/venv/bin/python common/make_ep.py <NN> [all|script|tts|timeline|render|mux|qc|yt|stills [t...]]` (C: `common_C/make_ep_c.py`). Stages recorded in `progress_A.json` / `progress_C.json` (fcntl lock); `all` skips stages already done.
- Queues: `EPS="02 03" tts_queue.sh` (waits for `epNN/src.ready`), `build_queue.sh` (waits for tts then `all`, `WORKERS` default 4); C: `tts_chain.sh <WAITPID> <eps>` and `build_chain.sh` (`WORKERS=2`).
- C differs from A: per-scene line ids `<scene>_NN`, scene-text md5 cache (`voice/scene_hash.json`) to re-synth only changed scenes, TTS via `align_ep.py` (energy_align split → per-line fallback, ratio bounds 0.6–1.6 for ≥20 chars else 0.4–2.2), workers 2, Whisper 2 threads.
- `make_ep.py` also symlinks `lemo-opuscar/films/epNN → epNN/film` and renders from inside the lemo-opuscar checkout.
### box pipeline B / D
- `cd <ep> && /workspace/venv/bin/python ../epB_engine/pipe.py . <steps|all>`; steps `tts timeline layout render mix srt md qc yt` (+ D: `master`, `pace.json`). Env `WK` = render workers (B default 3, D default 1).
- D `render()` has a **resource gate**: waits until <2 other `image2pipe` ffmpeg processes and >3.5 GB MemAvailable for two consecutive 30 s checks.
- Queues: B `ttsq.sh` (sequential TTS for eps listed in `ttsq.txt`), `postq.sh` (post steps one ep at a time; WK=2 only if no other render and >6 GB free); D `queue.sh` (tts loop ep18→20 ∥ post loop with WK=2), `post2.sh` (ep19/20 post with WK=1 + master), `prefetch.py <epdirs>` (synthesize scene chunks ahead of alignment → `voice/costs_pre.json`).
- `stills.py <epdir> [scene ids]` → end-of-scene stills + 2×2 contact sheets in `qc/pre/`. `zh.py` converts numbers to Chinese readings for `say=`.
- `lib.py` (Ep DSL) is identical in B and D; B uses `my_align.py` (whisper) while D uses `sil_split.py` (pauses).
### other tools
- `engine/qc/final_qc.py <epNN>` (desk_xfer/qc.py), `engine/qc/progress_update.py <progress file> <EPkey> '<json>'` (locked merge into progress JSON).
- `engine/tools/transcribe_refs.py` (`tr.py`): faster-whisper small int8 transcripts of 7 reference YouTube videos (style research; videos not included).
- `engine/tools/voice_test/` — the voice bake-off that chose Enceladus: `tts.py` (several OpenRouter TTS models on `passage.txt`), `gem.py` (Gemini synth helper also imported by ep01 scripts), `asr.py <model>` (Whisper back-check), `models.json` (OpenRouter model list snapshot), `results.json`.
- `engine/pipeline_A/sheet.sh dir out.jpg` (3-column contact sheet of `t_*.jpg`), `rec_drive.py <ep> <mp4url> <srturl>` (record Drive upload in progress_A).
- `coverage/build.py` → `coverage.xlsx` (sheets 覆蓋率摘要, 覆蓋檢查): hand-maintained table of (PART, page range, topic, planned EP, final EP, note) for handouts PART00–PART03; result 511/511 pages covered. Run with openpyxl: `cd coverage && python build.py`.

## 3. Directory contents
- `engine/pipeline_A/` make_ep.py, engine.js (src.py-format canvas renderer, Style A dark architecture diagram), build_queue.sh, tts_queue.sh, sheet.sh, rec_drive.py
- `engine/pipeline_C/` make_ep_c.py, align_ep.py, energy_align.py, or_align_c.py, tts_openrouter_c.py (copy of lemo overlay TTS with threaded prefetch + `SYNTH_ONLY`), tts_chain.sh, build_chain.sh
- `engine/pipeline_B/` pipe.py, lib.py, engine.js (DSL renderer, exposes `window.TEXTS`), layout.mjs, my_align.py, stills.py, ttsq.sh, postq.sh, ttsq.txt (queue list). Note: an empty flag file `linemode` existed in epB_engine to force per-line TTS — not copied.
- `engine/pipeline_D/` pipe.py, lib.py, engine.js (= B's), layout.mjs, my_align.py, sil_split.py, zh.py, prefetch.py, stills.py, queue.sh, post2.sh
- `engine/lemo_overlay/` our files that live inside the lemo-opuscar checkout + `LEMO_OPUSCAR.md` (commit `f17136060781a0068a7951245a3aa7835a7230de`, parts used).
- `engine/qc/`, `engine/tools/` see §2.
- `windows-kit/` full kit source: make_episode.py/.cmd/.sh, setup.ps1/.cmd/.sh, requirements*.txt, package(-lock).json, kit/ (lib.py, tts_openrouter.py, sil_split.py, whisper_align.py, whisper_util.py, zh.py), render/ (modified lemo-opuscar mjs + layout.mjs), engine/engine.js, assets/fonts (DejaVu only; see FONTS_NOT_INCLUDED.md), licenses/, README.md (zh-TW user guide, troubleshooting table), .env.example (placeholder), .gitignore, run_ep*.cmd, queue*.ps1, episodes/sample, episodes/ep13-example. Box copy verified identical (MD5) to `D:\ml-video-kit` for every shared file.
- `episodes/<ep>/` source only: `src.py` (EP00, 02–10) or `build.py` (EP11–20, A1, A2/p1, A2/p2) plus generated-but-small text: script.json, lines.json, scenes.json, meta.json, cues.json, script.md, epNN.srt, youtube.json, `voice/*.json` (dur/costs/align/match/scene_hash), `qc/*.json|txt`, `pace.json` (EP19). EP01 = prototype (script.py, scene_synth.py, voice_enc.py, align_split.py, align_test.py, line_check.py, two voice variants: HsiaoChen vs Enceladus cues/srt). EP12 also has `youtube_boxrender.json`, `sync_desktop.json`. EP18 has `build_B_draft.py` (B-engine draft before D took over). epA1/hw: Hunt's tree script + CSVs; epA2: `a2_hunt.py`, `a2_calc.py`, `a2_sklearn.py` + outputs.
  A1/A2 cues.json/script.md/youtube.json exist only on the desktop (`D:\ml-video-kit\episodes\epA1|epA2_1|epA2_2`) — copying them was refused (path outside the allowed root); they are regenerable with `make_episode timeline md yt`.
- `episodes/_worked_examples/` numeric ground truth used in scripts: epB_src/calc.py (entropy/Gini/error by hand), ep17_curve.*, ep18_cv.*, mk.py (handout-page contact sheets), titanic.csv; epD/ep18_calc.*, ep18_cv_B.py, ep18_cv_check.json, ep19_calc.py, titanic_sns.csv, a3/ (EP20 CART-on-Titanic run; needs pandas, seaborn, scikit-learn — box venv `epD/venv` had scikit-learn 1.9.1, pandas 3.1.0, seaborn 0.13.2, matplotlib 3.11.2, imbalanced-learn 0.14.2).
  Handout PDFs/page images/page texts (course material) were deliberately NOT included.
- `upload/` meta.json (per-ep title/tags/file, used by run_ep.sh), mac_stage/meta.json, `epNN_desc.txt` descriptions (already scrubbed of school name), run_ep.sh, do_ep.sh, record.py, youtube_uploads.json (24 entries, all private; host name redacted).
- `coverage/` build.py + coverage.xlsx (13 KB).
- `notes/` VOICE.md (voice default + mix limiter + fallback), season_plan.md (season plan, per-ep scope/minutes), `state/progress_*.json` (stage/QC/loudness/duration per ep; Drive links redacted), `state/watchdog_last_report.txt`, `logs/` (queue logs that show the watchdog restarts).

## 4. Dependencies (versions found on the box / kit)
- Python 3.13.5 (`/workspace/venv`); kit recommends 3.11 (3.10–3.13). Packages: faster-whisper 1.2.1, ctranslate2 4.8.4, av 18.1.0 (**must be <19**), numpy 2.5.4, soundfile 0.14.0, opencc-python-reimplemented 0.1.7, Pillow (stills), openpyxl (coverage). Optional CUDA: nvidia-cublas-cu12, nvidia-cudnn-cu12 9.x. Whisper model `small` (QC/align), `base` tried in B.
- Node v24.22.1 (kit requires ≥18; lemo ≥20), playwright-core 1.63.0, chromium_headless_shell-1243.
- ffmpeg 7.1.5 (Debian) on box; desktop: ffmpeg with h264_nvenc (winget Gyan.FFmpeg).
- Upload: `uv`, the Mac skill `roy-upload-video`.

## 5. Environment variables
`OPENROUTER_API_KEY` (required for TTS; kit reads it from `<kit>/.env`, never printed), `KIT_WORKERS`, `KIT_NVENC=1`, `KIT_WHISPER_DEVICE`, `KIT_TTS_VOICE`, `KIT_TTS_MODEL`, `KIT_VCODEC=nvenc` (set internally for video.mjs), `PLAYWRIGHT_BROWSERS_PATH`, `HF_HOME`, `HF_HUB_DISABLE_SYMLINKS_WARNING`, `LEMO_ANGLE` (lemo browser backend), `RENDER_SLOTS` (lemo video.mjs), box pipelines: `WORKERS` (A/C), `WK` (B/D), `EPS` (queues), `FAKE` (A/C timeline dry estimate 0.27 s/char), `SYNTH_ONLY` (C TTS).

## 6. Upload interface (Mac skill, not included)
On Boss's MacBook, files staged in `~/Documents/roy-ai-editor/yt_inbox/` (mp4 + `epNN_desc.txt` + `meta.json`):
- preflight: `uv run roy-editor youtube preflight`
- `upload/run_ep.sh NN [--dry-run]` → `uv run python ~/.claude/skills/roy-upload-video/scripts/upload.py --file <inbox>/<file> --title <title> --description-file <inbox>/epNN_desc.txt --tags "<comma tags>" --lang zh-TW --synthetic yes [--dry-run]`; refuses (exit 3) if title/tags/desc contain the school name.
- `upload/do_ep.sh NN`: dry-run → expects `"dry_run"` (or `"already_uploaded"`), then real upload; deletes the local mp4 after `"status": "uploaded"`.
- Output JSON fields used: `status`, `url`, `metadata.title`. Videos are uploaded **private**; playlist ordering done manually in YouTube Studio in a browser (the API token is upload-only). `record.py` appended results into `youtube_uploads.json`. Credentials for the skill live on the Mac only.

## 7. Hard-coded paths to parameterize
- `/workspace/video_style` (ROOT/VS) and `/workspace/video_style/lemo-opuscar` (LEMO/LIB): pipeline_A/C make_ep*.py, all *.sh queues, B/D pipe.py, layout.mjs (absolute import of `page.mjs`), stills.py, prefetch.py, tts_openrouter_c.py, qc scripts, record.py.
- `/workspace/venv/bin/python` (PY) and `lemo-opuscar/.venv/bin/python` (LPY): A/C/B/D + queues.
- Episode `build.py` first line `sys.path.insert(0,'/workspace/video_style/epB_engine'|'epD_engine')`; EP17/18/20 read `/workspace/video_style/epB_src/*.json`, `epD/ep18_calc.json`, `epD/a3/a3.json` (now in `episodes/_worked_examples/`).
- `/workspace/video_style/voice_test` (ep01 scripts), fixed temp files `/tmp/seg_A.wav`, `/tmp/seg_C.wav`, `/tmp/sl.txt`, `/tmp/al`.
- Progress JSON file names (progress_A/B/C/D) hard-coded per pipeline; postq.sh greps `video.mjs /workspace/video_style/ep1[1-7]/film`.
- Windows: `D:\ml-video-kit` in run_ep*.cmd and queue*.ps1. Mac: `~/Documents/roy-ai-editor/yt_inbox`, `~/.claude/skills/roy-upload-video/...`.
- make_episode.py `about` default text (series blurb) and the B/D `yt()` blurb are hard-coded strings.

## 8. Known gotchas (from logs/notes)
- **OpenRouter HTTP 429** constantly (≈150 retry lines across logs): code backs off (tts_openrouter tries 12–20, pipe.py extra 60→600 s loop). Also `The read operation timed out` (6×). ~15 requests per episode. Prefetching scene audio (`prefetch.py`, C threaded prefetch) hides the latency.
- **Scene→line split failures**: `alignment failed between line 0 and 1: None None` (hook/quiz/greedy/title scenes), `ValueError: attempt to get argmin of an empty sequence` (4×), whisper `low match [0.0…]` → per-line synthesis fallback. EP17 was finally done with `--tts-mode line`.
- **Screenshot timeouts**: `render stopped: page.screenshot: Timeout 30000ms exceeded.` (5×) when the 8-core/15 GB box was overloaded by parallel renders → keep **≤2 render workers total** on the box; D added the image2pipe/MemAvailable gate; queues serialize renders.
- **Worker overload / watchdog**: an agent watchdog routine (not a script) restarted failed builds (`common_C/queue.log`: "BUILD FAIL 09/10 … watchdog restart/2/3"), moved desktop-owned eps (12/16/17) out of the box queue and killed duplicate box renders (`postq.log`/`ttsq.log` "Terminated"); `*.bak_watchdog*` files were its edits (e.g., a precedence bug fix in align_ep.py's ratio check). Last report: `watchdog_last_report.txt`.
- **NVENC session limit** (RTX 3060 Ti, consumer driver): only one NVENC render at a time on the desktop (`progress_A12.json` note) and ≤5–6 workers per render; hence queue*.ps1 serialization.
- **Loudness**: Gemini TTS peaks are hot → limiter before mux is mandatory (VOICE.md); mux sometimes misses (EP03 −0.9 dBTP warn; desktop EP16/17/19 "[mux] warning: missed -14 LUFS") → the `master` step fixes it.
- **WebGL software rendering** warning on the box (llvmpipe) raised an AssertionError in a strict page check; the canvas-2D engine itself does not need WebGL.
- **av 19** breaks faster-whisper 1.2 (`TypeError: metadata_errors`) → pin `av<19`.
- Whisper homophone false alarms in sync QC (信→性, 序章→續章) — listen by ear. QC sync similarity today: 0.78–0.96 (C eps lowest).
- Windows: video file locked if open in a player (`PermissionError`), stale `out\video.mp4.lock` after crashed render.
- Never put the school name in tags/description (run_ep.sh guard); descriptions use 「依大學『機器學習』課程講義」.

## 9. Scrubbing done for this bundle
- Secret scan (`sk-or-|api_key|token|Bearer|password|client_secret|refresh_token`): only env-var references / placeholder checks remained; no key values. `.env` files excluded; `windows-kit/.env.example` has `OPENROUTER_API_KEY=your-key-here`.
- Removed the school-name tag from every tags list (B/D/kit `build.py`, meta.json, youtube.json) and replaced the blurb text in B/D `pipe.py`, kit `make_episode.py` and youtube.json with 「依照大學「機器學習」課程講義整理」. The only remaining occurrence is the blocking guard regex in `upload/run_ep.sh`.
- Mac host name → `<mac-hostname>`; Google Drive file/folder links → `<drive-link-redacted>`.
- Excluded: all media, Noto CJK fonts (23.5 MB → side archive `/workspace/repo_bundle_fonts.tar.gz` on the box), handout PDFs/images/texts, venvs, node_modules, __pycache__, lemo-opuscar itself, `*.bak*`, run logs (summarized in §8), anything from `~/Library/Application Support/RoyAIEditor` or the keychain (never touched).

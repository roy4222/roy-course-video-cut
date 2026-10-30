# legacy：歷史管線（不要拿來做新的一集）

這裡是 2026-10-30 當天，在同一台機器上平行用過的四代舊工具。它們和 `windows-kit/` 做的是同一件事（腳本 → 配音 → 畫面 → 成片），但是入口、檔名、路徑都不一樣。

**新的一集請用 [`windows-kit/`](../windows-kit/README.md)。** 套件的 `make_episode.py` 已經把後來能用的步驟收成一個指令。

| 資料夾 | 當年做了哪些集 | 集數腳本長什麼樣子 |
|---|---|---|
| `pipeline_A/` | EP00、EP02–EP05 | `episodes/epNN/src.py` 裡的 `META` + `SCENES` |
| `pipeline_C/` | EP06–EP10 | 同上，多了「只重錄改過的場景」 |
| `pipeline_B/` | EP11、EP13、EP15，以及 12／14／16／17 的第一稿 | `build.py`，用 `lib.Ep` |
| `pipeline_D/` | EP18、EP20 | 同 B，多了 `master` 與 `pace.json` |
| `qc/` | 事後檢查與進度檔合併 | `final_qc.py`、`progress_update.py` |
| `tools/` | 選聲音、轉寫參考片 | `voice_test/`、`transcribe_refs.py` |
| `lemo_overlay/` | 放進 lemo-opuscar 裡的我們自己的 TTS | 不是上游的程式 |

EP00–EP10 的 `src.py` 畫面引擎和套件裡的 `engine.js` 不同。套件讀不了那種格式。要重做，先改寫成 `build.py`。

## 路徑

這些腳本預設仍指向當天那台機器的目錄（`/workspace/video_style`、`/workspace/venv/bin/python`）。沒有設定環境變數時，行為和當天一樣。換機器時用環境變數改，不必改程式：

| 變數 | 沒設定時 | 用途 |
|---|---|---|
| `VIDEO_STYLE_ROOT` | `/workspace/video_style` | 舊管線的根目錄 |
| `LEMO_OPUSCAR` | `$VIDEO_STYLE_ROOT/lemo-opuscar` | lemo-opuscar 的位置 |
| `LEMO_PAGE_MJS` | 上面那個 checkout 的 `core/render/page.mjs` | B／D 的版面檢查 |
| `VIDEO_STYLE_PYTHON` | `/workspace/venv/bin/python` | 當天的 Python |
| `LEMO_PYTHON` | lemo checkout 裡的 `.venv/bin/python` | 跑上游的 `srt.py` |
| `EP_ENGINE` | `…/epB_engine` 或 `…/epD_engine`（看是 B 還是 D） | `lib.py` 所在目錄 |
| `PIPELINE_TMP_WAV_A` / `_C` | `/tmp/seg_A.wav`、`/tmp/seg_C.wav` | 品質檢查暫存音檔 |
| `PIPELINE_TMP` | `/tmp` | `sheet.sh` 的清單檔 |
| `WORKERS`、`WK`、`EPS` | 各佇列腳本自己的預設 | 渲染工人數、要跑哪些集 |

佇列腳本（`build_queue.sh`、`postq.sh` 那些）還假設根目錄下面有當天的資料夾名字：`common/`、`epB_engine/`、`ep11/`。這個倉庫把它們收成 `legacy/pipeline_*` 和 `episodes/ep11/`，所以**只改 `VIDEO_STYLE_ROOT` 還不夠把佇列原樣跑起來**。要對照當天的行為，把變數指回仍保留舊資料夾名稱的那份目錄。

怎麼取得釘選的 lemo-opuscar，見 [docs/lemo-opuscar.md](../docs/lemo-opuscar.md)。

逐檔說明（英文）在 [INVENTORY.md](../INVENTORY.md)。那份清單寫於整理之前，提到的 `engine/` 就是現在的 `legacy/`。

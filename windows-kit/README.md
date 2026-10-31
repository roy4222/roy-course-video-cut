# ml-video-kit：機器學習補習影片產線（可攜版）

> 這是 **v1** 產線（機器學習從零開始），也是 v2 算圖時呼叫的畫面引擎。程式留在這個資料夾，沒有搬進 `pipeline/v1/`。2026-10-30 更早的實驗在倉庫的 `legacy/`。系統與軟體安全的流程在 [`pipeline/v2/`](../pipeline/v2/README.md)。繁中 Noto 字型沒有放進 git，請先跑倉庫根目錄的 `scripts/fetch_fonts.ps1`（或 `scripts/fetch_fonts.sh`）。

把「腳本＋畫面描述」（一個集數資料夾）一路做成 **1080p30、燒錄繁中字幕、−14 LUFS** 的成片、`.srt` 字幕檔與 YouTube 上架資訊。

流程：`build.py`（腳本＋畫面）→ OpenRouter Gemini TTS（聲音 Enceladus，台灣華語老師語氣）→ 時間軸 → HTML canvas 畫面由無頭 Chromium（Playwright）逐格截圖 → ffmpeg 編碼 → 混音、限幅、響度標準化 → 成片。

> 套件內**沒有**任何 API 金鑰、集數影音或特定機器的路徑。金鑰只放在你自己電腦的 `.env`。

---

## 1. 系統需求

| 項目 | 需求 | 備註 |
|---|---|---|
| 作業系統 | **Windows 10/11**（主要）、Linux；macOS 應可用（未實測） | |
| CPU / RAM | 4 執行緒、8 GB 起跳 | 參考機 i7-13700F（24 執行緒）/ 48 GB：預設 6 個渲染 worker |
| 硬碟 | 安裝約 2.5 GB（Python 套件、Chromium、Whisper 模型）＋每集約 0.5–1 GB 暫存 | 建議放 `D:\ml-video-kit` |
| Python | 由 setup 透過 **uv** 自動安裝 **Python 3.11**（放在 `.venv`） | 不會動到 `C:\Python38` |
| Node.js | 18 以上 | 沒有的話 setup 會用 winget 安裝 |
| ffmpeg | 需含 ffprobe；有 NVIDIA 顯卡時建議用含 `h264_nvenc` 的完整版（scoop / gyan.dev 版本都有） | 沒有的話 setup 會用 winget 安裝 |
| 網路 | 只有 TTS（OpenRouter）與第一次安裝需要 | 渲染、混音完全離線 |
| NVIDIA 顯卡（選用） | RTX 3060 Ti 等：`--nvenc` 用 GPU 編碼；`-Cuda` 讓 Whisper 用 GPU | 都是選用，CPU 也能完整跑完 |

## 2. 安裝（Windows）

1. 把這個 `windows-kit` 資料夾放在你要的位置（下面用 **`D:\ml-video-kit`** 當例子）。`run_ep.cmd` 和 `queue*.ps1` 會用腳本自己所在的資料夾；若要改，設環境變數 `ML_VIDEO_KIT`。
2. 開 PowerShell（不需要系統管理員），執行：

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File D:\ml-video-kit\setup.ps1
   # 有 NVIDIA 顯卡、想讓 Whisper 也用 GPU：
   powershell -NoProfile -ExecutionPolicy Bypass -File D:\ml-video-kit\setup.ps1 -Cuda
   ```

   或直接雙擊 `setup.cmd`。setup **不會問任何問題、可以重複執行**（已裝好的會跳過），依序做：
   uv → Python 3.11 venv＋套件 → Node 套件 → Chromium（裝在 `D:\ml-video-kit\.browsers`）→ 檢查 ffmpeg / NVENC → 下載 Whisper small 模型（放在 `D:\ml-video-kit\.cache`）→ 建立 `.env`。
3. 打開 `D:\ml-video-kit\.env`，把 `OPENROUTER_API_KEY=your-key-here` 換成你的 OpenRouter 金鑰。

Linux / macOS：`bash setup.sh`（`--cuda` 同上）。缺 ffmpeg 時：`sudo apt install -y ffmpeg`（Debian/Ubuntu）、`brew install ffmpeg`（macOS）。

## 3. 煙霧測試（不需要金鑰、不花錢）

```powershell
cd D:\ml-video-kit
.\make_episode.cmd episodes\sample
```

範例集已附好旁白音檔，所以 TTS 會直接跳過。約 1–3 分鐘後得到：
`episodes\sample\ep99.mp4`（約 40 秒、3 個場景）、`ep99.srt`、`youtube.json`、`script.md`、`qc\`（截圖與同步檢查）。

想順便測 TTS（約 US$0.01）：刪掉 `episodes\sample\voice` 資料夾再跑一次。

## 4. 做一集：單一指令

```powershell
cd D:\ml-video-kit
.\make_episode.cmd D:\videos\ep21                 # 從頭到尾（已完成的步驟自動跳過）
.\make_episode.cmd D:\videos\ep21 --nvenc         # 用 NVIDIA GPU 編碼（較快）
.\make_episode.cmd D:\videos\ep21 --workers 8     # 指定渲染 worker 數
```

（Linux/macOS：`./make_episode.sh <集數資料夾>`；任何系統也都可以 `.venv\Scripts\python make_episode.py <集數資料夾>`。）

### 步驟（預設全部依序執行）

| 步驟 | 做什麼 | 產出 |
|---|---|---|
| `build` | 執行集數資料夾裡的 `build.py` | `script.json`、`scenes.json`、`meta.json` |
| `tts` | 每個場景一次 TTS 請求，再切回每一句（先用停頓切，不準再用 Whisper 對齊，仍不準就逐句重錄） | `voice\l000.wav…`、`voice\dur.json`、`voice\costs.json` |
| `timeline` | 依每句長度排時間軸、產生網頁 | `film\index.html`、`film\timeline.js`、`cues.json` |
| `layout` | 檢查文字重疊、出界、被字幕擋住（只警告） | `qc\layout.txt` |
| `render` | Chromium 逐格截圖 → ffmpeg（字幕已燒在畫面上） | `out\video.mp4` |
| `mix` | 把每句旁白放到時間軸上＋限幅 | `out\mix_lim.wav` |
| `mux` | 合成影音、兩段式 loudnorm 到 −14 LUFS / −1.2 dBTP | `epNN.mp4` |
| `master` | 最後的峰值限幅、AAC 192k、faststart | `epNN.mp4`（原地更新）、`qc\loudness.json` |
| `srt` | 字幕檔 | `epNN.srt` |
| `md` | 帶時間碼的可讀腳本 | `script.md` |
| `qc` | 8 張截圖＋Whisper 抽聽 3 句檢查音畫同步 | `qc\f*.jpg`、`qc\sync.json` |
| `yt` | YouTube 標題、說明（含章節時間）、標籤 | `youtube.json` |
| `stills`（額外） | 每個場景結尾的預覽圖，寫腳本時很好用 | `qc\pre\s_*.jpg` |

**可續跑**：每個步驟完成會在 `.kit\` 留記號；中斷（關機、斷網、429）後再下同一個指令，會從沒完成的地方繼續。TTS 逐句快取（以文字雜湊比對），只會重錄改過的句子；`render` 被中斷時會清掉暫存片段重來。

**只跑某些步驟**（指名的步驟一定重跑）：

```powershell
.\make_episode.cmd D:\videos\ep21 build timeline stills    # 改畫面後先看預覽圖，不花 TTS 錢
.\make_episode.cmd D:\videos\ep21 render mix mux master    # 只重做影像
.\make_episode.cmd D:\videos\ep21 --force                  # 全部重做（TTS 仍沿用快取的音檔）
```

其他參數：`--tts-mode line`（每句一個請求，較貴但最穩）、`--whisper-device cuda|cpu|auto`、`--low-priority`（降低優先權，邊做影片邊用電腦）。`.env` 也可以設定預設值（見 `.env.example`）。

## 5. 集數資料夾格式

一集 = 一個資料夾，最少只要一個 `build.py`：

```
ep21\
  build.py        ← 你寫的：腳本＋畫面（必要）
  pace.json       ← 選用：{"line": 0.7, "scene": 1.2} 句與句、場景與場景之間的空白秒數
  （以下都是自動產生）
  script.json scenes.json meta.json lines.json   ← build.py 產生
  voice\  film\  out\  qc\  .kit\  pipe.log       ← 中間檔、記錄
  ep21.mp4  ep21.srt  script.md  youtube.json     ← 成品
```

範例：`episodes\sample\build.py`（3 個場景，最小可用）、`episodes\ep13-example\build.py`（第 13 集完整腳本，可以直接做出整集，TTS 約 US$0.1–0.3）。

### build.py 寫法

```python
from lib import Ep            # 不用寫路徑，make_episode 會處理
ep = Ep(21, '標題', '',       # 集數、標題、頁首（空字串 = 自動「EP21 · 標題」）
        '一段摘要（放進 YouTube 說明）', ['標籤1', '標籤2'], '下集預告文字')
E = ep.E; L = ep.L

ep.scene('hook', '場景標題', chapter='YouTube 章節名', desc='畫面說明（寫進 script.md）', ref='講義 PART03 p38')
a = L('一句旁白，也就是畫面上的字幕。')
b = L('字幕寫 Hunt\'s 演算法', '念成：杭特演算法')        # 第二個參數 say = 實際念法（數字、英文、破音字）
c = L('停頓一下讓觀眾想想。', gap=2.0)                     # gap = 這句之後多停幾秒
E('card', x=150, y=220, w=620, h=120, title='跟著第 a 句出現', col='A', at=a)
E('text', s='第 b 句後 1.2 秒出現、第 c 句消失', x=960, y=600, size=34, align='center', at=[b, 1.2], until=c)

ep.save('.')                   # 一定要有：寫出 script.json / scenes.json / meta.json
```

- 畫布 1920×1080；頁首佔上方約 170px，字幕在下方約 y>900，內容放在 y≈200–880。
- `at=i`：第 i 句（本場景內從 0 起算）開始時淡入；`at=[i, 秒]` 再延後；`at=-1` 場景一開始就出現；`until=` 同格式，到時淡出。
- 顏色：`A`藍、`B`橘、`OK`綠、`BAD`紅、`PUR`紫、`CY`青、`INK`白、`DIM`灰，或直接 `'#rrggbb'`。
- 場景選項：`noHeader=True`（標題卡用）、`tag='作業一'`、`tagCol='B'`。
- 數字念法小工具：`from zh import zh, pct`（`zh(83.8)` → 八十三點八）。
- 存檔時會檢查每個 `at` 是否指到存在的句子。

### 畫面元素（`E(type, …)`）

| type | 主要參數 | 用途 |
|---|---|---|
| `titlecard` | `ep, title, sub` | 片頭標題卡 |
| `text` | `s, x, y, size, col, w(字重), align, wrap(寬度→自動換行), mono` | 單行／段落文字 |
| `card` | `x, y, w, h, title, ts, sub, body=[…], col, fill, align` | 卡片框 |
| `bullets` | `x, y, w, size, items=[{s, at, col}]` | 編號條列 |
| `chips` | `y, items=[{s, col, at}], size, cx` | 一排標籤 |
| `table` | `x, y, ws=[欄寬], head, rows, rh, hh, fs, rowAt, cellCol, fills, dim, bold` | 表格（逐列出現、儲存格上色） |
| `formula` | `x, y, w, lines, label, size` | 公式／計算步驟 |
| `tree` | `nodes=[{id,x,y,label,leaf,at}], edges=[{a,b,label}], path=[{ids,at}]` | 決策樹／樹狀圖（可走路徑） |
| `flow` / `blocks` / `arrow` / `line` | `flow`：`x, y, w, items=[{…, at}]`；其餘見 `episodes\ep13-example` 與 `engine\engine.js` | 流程圖、方塊、箭頭 |
| `bars` / `plot` / `dots` / `circle` | `x, y, w, h, items` / `xr, yr` … | 長條圖、散佈圖 |
| `code` | `x, y, w, h, title, cells=[{code=[每行…], out=[輸出行…], at}]` | 程式碼畫面（風格 C） |
| `quiz` | `y, qs=[{q, a, qi(題目句), ai(答案句)}]` | 小測驗（倒數後出答案） |
| `hl` / `check` / `cross` | `x, y, w, h, col` / `x, y, s` | 螢光框、打勾、打叉 |

完整的繪製邏輯在 `engine\engine.js`（每個 `R.<type>=` 就是一種元素）。

### 本機舊集數

- **EP11–EP20** 的 `build.py` 可以直接搬過來用（第一行舊的 `sys.path.insert(...)` 留著也沒關係）；已經錄好的 `voice\*.wav` 一起複製過來就不會重錄。
- **EP00–EP10** 用的是較早的 `src.py` 格式（另一套畫面引擎），本套件沒有收錄；要重做需先改寫成 `build.py`。

## 6. 效能調整

### 渲染 worker（`--workers N`）

每個 worker = 一個 Chromium＋一個 ffmpeg，各自渲染影片的一段，最後無損接起來。

- 預設自動：`min(8, CPU 執行緒 ÷ 4, RAM GB ÷ 6)`。i7-13700F / 48 GB → **6**。
- 每個 worker 約吃 2–4 個執行緒、1–1.5 GB RAM。
- 電腦專門跑影片：`--workers 8`；邊工作邊跑：`--workers 4 --low-priority`。
- 工作管理員 CPU 長時間 100%、或 RAM 用量超過 80%：調低。
- 也可以在 `.env` 寫 `KIT_WORKERS=8` 當預設。

### NVIDIA GPU

- **編碼（`--nvenc`）**：中間片段與成片都改用 `h264_nvenc`，CPU 省下來給 Chromium。需要 ffmpeg 有 `h264_nvenc`（setup 會檢查）。GeForce 驅動同時可開的 NVENC 編碼數有上限（新驅動 8 個、舊驅動 3–5 個）；`--nvenc` 時如果 render 失敗，改用 `--workers 5` 以下。
- **Whisper（`setup.ps1 -Cuda` 後加 `--whisper-device cuda`）**：TTS 切句與 QC 用的語音辨識改跑 GPU；CUDA 載入失敗會自動退回 CPU。Whisper 在整條產線中佔的時間不多，這是錦上添花。
- Chromium 在 Windows 本來就會用 GPU 畫 canvas，不需設定。

## 7. 疑難排解

| 狀況 | 處理 |
|---|---|
| `setup.ps1` 無法執行（「已停用指令碼」） | 用 `powershell -ExecutionPolicy Bypass -File ...`，或雙擊 `setup.cmd`；從網路下載的 zip 可先 `Unblock-File D:\ml-video-kit\*.ps1` |
| `"ffmpeg" was not found on PATH` | `winget install Gyan.FFmpeg` 或 `scoop install ffmpeg`，**開新的 PowerShell** 再跑 |
| `uv` / `node` 剛裝好卻找不到 | 關掉 PowerShell 重開（PATH 才會更新），再跑一次 setup |
| `OPENROUTER_API_KEY is not set` | 編輯 `.env`；金鑰不要加引號或空白 |
| TTS 一直出現 `HTTP 429` | 上游限流，程式會自動等待重試（最長 90 秒一次）；中斷了就再跑同一個指令，已錄好的不會重錄 |
| `HTTP 401/402/403` | 金鑰錯誤或 OpenRouter 餘額不足 |
| 某句聲音被切錯／念錯 | 修改該句（或加 `say=` 念法）後重跑：只有那個場景會重錄；或刪掉 `voice\l0xx.wav` 再跑 `tts` 以後的步驟 |
| `window.READY never became true`、`[pageerror]` | `build.py` 參數有誤（例如元素少了必要欄位），先跑 `build timeline stills` 看錯誤訊息 |
| `another render ... is already writing` | 上次 render 當掉留下的鎖：刪除 `out\video.mp4.lock` |
| `--nvenc` 時 `ffmpeg failed for worker` | NVENC 編碼數上限或驅動太舊：`--workers 4`，或拿掉 `--nvenc` |
| 渲染很慢、電腦很卡 | 降低 `--workers`，加 `--low-priority` |
| `qc\layout.txt` 有 OVERLAP / UNDER-SUBTITLE | 調整該元素的 x / y / w；這只是警告，不會擋住出片 |
| 響度不是 −14 | 看 `pipe.log` 的 `[mux]`、`[master]` 行；`qc\loudness.json` 有最終數值 |
| Linux 上 Chromium 缺 `.so` | `sudo node node_modules/playwright-core/cli.js install-deps chromium-headless-shell` |
| `PermissionError` / 無法覆寫 `epNN.mp4` | 影片正在播放器裡開著（Windows 會鎖檔）：關掉播放器再跑 |
| Whisper 第一次很慢 | 第一次要下載模型（約 0.5 GB）；setup 已預先下載到 `.cache\` |

執行紀錄都在集數資料夾的 `pipe.log`。

## 8. 檔案結構

```
ml-video-kit\
  make_episode.py      唯一入口（make_episode.cmd / make_episode.sh 是包裝）
  setup.ps1 / setup.cmd / setup.sh
  requirements.txt  requirements-cuda.txt  package.json  package-lock.json  .env.example
  kit\                 Python：TTS（tts_openrouter.py）、切句（sil_split.py、whisper_align.py）、Ep DSL（lib.py）、數字念法（zh.py）
  render\              Node：video.mjs（多 worker 渲染）、still.mjs、layout.mjs、page.mjs、serve.mjs、browser.mjs
  engine\engine.js     畫面引擎（風格 A：暗色架構圖）
  assets\fonts\        DejaVu Sans Mono 已內建；Noto Sans CJK TC 用倉庫的 scripts/fetch_fonts 下載（見 FONTS_NOT_INCLUDED.md）
  episodes\sample\     煙霧測試用範例集（含旁白音檔）
  episodes\ep13-example\  完整一集的 build.py 範例
  licenses\            第三方授權（lemo-opuscar MIT、字型 OFL 等）
```

## 9. 授權與來源

- 渲染核心改自 lemo-opuscar（MIT，見 `licenses\`）。
- 字型：Noto Sans CJK TC（SIL OFL 1.1）、DejaVu Sans Mono（Bitstream Vera 授權）。
- 旁白為 AI 合成語音（OpenRouter `google/gemini-3.8-flash-tts`，voice Enceladus）；`youtube.json` 已標示 `synthetic: true`。

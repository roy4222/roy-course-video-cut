# lemo-opuscar

渲染用的無頭瀏覽器、靜態網頁伺服器、截圖，來自 [lemomo-ai/lemo-opuscar](https://github.com/lemomo-ai/lemo-opuscar)，授權是 MIT。

**整份上游沒有放進這個倉庫。** 我們用的 commit 是：

`f17136060781a0068a7951245a3aa7835a7230de`

（2026-10-29，「Merge #10 from waiting761: Chinese numerals in asr_check」。）

`windows-kit/` 做片**不必**先抓這份上游。套件裡的 `render/*.mjs` 已經是改過的副本：`serve.mjs` 與上游相同，其餘差幾行到十幾行（例如片段編碼看 `KIT_VCODEC=nvenc`）。每個副本檔案開頭有 LemoLab 的著作權聲明，全文在：

`windows-kit/licenses/lemo-opuscar-MIT.txt`

請把這份授權留在套件裡。你若再複製 `render/` 的程式，連同這個聲明和授權檔一起複製。

## 什麼時候才要抓上游

`legacy/` 裡的舊管線會呼叫 checkout 裡的 `core/render/video.mjs`、`still.mjs`、`page.mjs`、`mux.sh`、`srt.py`。要原樣對照舊管線時才需要抓。

我們加在上游目錄裡、不屬於上游的檔案，拷貝在 `legacy/lemo_overlay/`：

- `core/tts/tts_openrouter.py`
- `core/tts/or_align.py`
- `core/tts/or_silence.py`
- `core-README.md.patch`（上游 README 上多了幾行，說明預設聲音）

## 下載

在倉庫根目錄：

```bash
bash scripts/fetch_lemo_opuscar.sh
```

Windows：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_lemo_opuscar.ps1
```

腳本會把倉庫 clone 到 `third_party/lemo-opuscar`（或你設的 `LEMO_OPUSCAR`），`git fetch` 上面那個 commit，再 checkout。接著把 `legacy/lemo_overlay/core/tts/*.py` 複製進去。這個目錄在 `.gitignore` 裡。

第一次使用：

```bash
npm --prefix third_party/lemo-opuscar ci
export LEMO_OPUSCAR="$PWD/third_party/lemo-opuscar"
```

手動做同一件事：

```bash
git clone https://github.com/lemomo-ai/lemo-opuscar.git third_party/lemo-opuscar
git -C third_party/lemo-opuscar fetch --depth 1 origin f17136060781a0068a7951245a3aa7835a7230de
git -C third_party/lemo-opuscar checkout --detach FETCH_HEAD
cp legacy/lemo_overlay/core/tts/*.py third_party/lemo-opuscar/core/tts/
```

## 用 submodule 釘同一個 commit

若你希望 `git clone --recurse-submodules` 就帶到這個 commit，可以改用 submodule（二選一，不要兩種都提交）：

```bash
git submodule add https://github.com/lemomo-ai/lemo-opuscar.git third_party/lemo-opuscar
git -C third_party/lemo-opuscar fetch --depth 1 origin f17136060781a0068a7951245a3aa7835a7230de
git -C third_party/lemo-opuscar checkout --detach FETCH_HEAD
git add .gitmodules third_party/lemo-opuscar
```

這個倉庫目前用下載腳本，而不是 submodule，因為套件本身不依賴那份完整目錄，也少一個初學者容易忘記的 `--recurse-submodules`。

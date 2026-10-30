# 維護這個倉庫

讀這份的人，就是以後要繼續加畫面效果、做新的一集的人。你不需要先懂全部歷史管線。平常只改 `windows-kit/` 和 `episodes/`。

## 先看哪裡

1. 根目錄 `README.md`：整條流程、怎麼裝、怎麼做一集。
2. `windows-kit/README.md`：安裝細節和錯誤對照表。
3. `docs/`：腳本格式、配音、渲染、上傳、之後想做的題目。
4. `INVENTORY.md`：2026-10-30 當天每個檔案在做什麼（英文）。整理之後 `engine/` 改名成 `legacy/`。

## 改程式時請守住的事

- **新功能加在 `windows-kit/`。** `legacy/` 是當天留下的四代工具。可以修到能在別台機器上對照（環境變數已經留好），不要拿它做新的一集。
- **能跑的程式不要為了好看重寫。** 路徑若寫死，用環境變數加上原本的預設值，沒設定時行為要和原本一樣。
- **一種新的畫面元素**加在 `windows-kit/engine/engine.js` 的 `R.<名字>`。寫法見 [docs/episode-format.md](docs/episode-format.md)。
- **改了步驟的行為**（時間軸、響度、配音重試），請在 `CHANGELOG.md` 加一筆，並在 `docs/` 對應的那一頁改掉，避免說明和程式各說各話。
- 依賴版本：`faster-whisper` 搭配的 `av` 必須 **小於 19**（`windows-kit/requirements.txt` 已釘 `av>=12,<19`）。Playwright 用 `playwright-core` 1.63.0，和 `package-lock.json` 一起走 `npm ci`。

## 不要 commit 的東西

`.gitignore` 已經擋了這些。送出之前再看一眼 `git status`：

- `.env`、任何 API 金鑰、`sk-or-` 開頭的字串
- `.venv/`、`node_modules/`、`__pycache__/`
- `.browsers/`、`.cache/`（Chromium 與 Whisper 模型）
- 成片和中間檔：`*.mp4`、`*.wav`、`*.png`、`*.jpg`、各集的 `film/`、`out/`
- Noto CJK 的 woff2（用 `scripts/fetch_fonts.sh` 或 `.ps1` 在自己電腦下載）
- `third_party/lemo-opuscar/`（用 `scripts/fetch_lemo_opuscar.sh` 取得）
- 課程講義的 PDF、頁面圖、頁面文字。覆蓋率表 `coverage/` 可以留，講義本身不要加回來。

這個倉庫是**公開**的。上傳紀錄 `upload/youtube_uploads.json` 裡的影片 ID 是佔位符。真實 ID 只留在你自己的上傳電腦，不要貼回 git。標題、標籤、說明維持「大學課程講義」這種寫法。`upload/run_ep.sh` 裡已有一段檢查，出現學校名稱就會停止（exit 3）。那段檢查留在那個檔案，不要把學校名稱抄到別的檔案。

## 送出前

1. 對改過的 Python 跑 `python3 -m py_compile <檔案>`。
2. 對改過的 shell 跑 `bash -n <檔案>`。
3. 自己搜一次秘密，例如：

   ```bash
   git grep -n -E 'sk-or-v1-[0-9A-Za-z]{8,}|ghp_|github_pat_|BEGIN [A-Z ]*PRIVATE' || echo "no key-shaped strings"
   ```

4. 若改到畫面或步驟，用 `windows-kit` 的範例集走一次你改到的步驟（見 README 的快速開始）。範例集的音檔沒有放在 git 裡，沒有金鑰時可以只跑 `build timeline stills` 看畫面。
5. 在 `CHANGELOG.md` 寫下使用者會感覺到的變化。

## 分支

小改動可以直接留在你正在用的分支。說明寫清楚「改了哪個步驟、怎麼確認」。

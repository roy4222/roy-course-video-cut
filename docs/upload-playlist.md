# 上傳與播放清單

成片、`.srt`、`youtube.json` 做出來之後，上傳在 Mac 上做。上傳用的那支程式（`roy-upload-video`）沒有放進這個倉庫，憑證也只在那台 Mac。

影片以**私人**上傳。YouTube 的 API 權限只有上傳，**播放清單要在 YouTube Studio 的瀏覽器裡自己排**。

## `youtube.json` 裡有什麼

`yt` 步驟會寫：

- 標題：`機器學習從零開始 EPNN｜<這一集的標題>`
- 說明：摘要、章節（場景開始時間減 0.9 秒，兩章至少相隔 10 秒）、一段系列介紹
- 標籤、`synthetic: true`、`language: zh-TW`、分類 Education
- 成片與字幕的檔名

套件在寫這個檔之前會檢查：說明裡不能出現本機路徑、很長的亂碼、或 `sk-or-`。

`upload/meta.json` 是給上傳腳本看的標題、標籤和檔名。`upload/epNN_desc.txt` 是說明本文。`upload/mac_stage/meta.json` 是同一份資料的另一份拷貝，給放到 Mac 收件匣時用。

## 在 Mac 上怎麼跑

檔案先放到收件匣：一支 mp4、對應的 `epNN_desc.txt`、還有 `meta.json`。

預設收件匣是 `~/Documents/roy-ai-editor/yt_inbox`。換位置時設環境變數，不必改腳本：

| 變數 | 沒設定時 |
|---|---|
| `YT_EDITOR_ROOT` | `~/Documents/roy-ai-editor` |
| `YT_INBOX` | `$YT_EDITOR_ROOT/yt_inbox` |
| `YT_UPLOAD_PY` | `~/.claude/skills/roy-upload-video/scripts/upload.py` |
| `YOUTUBE_UPLOADS_JSON` | `upload/youtube_uploads.json`（跟 `record.py` 放在一起時） |

流程：

1. 在編輯器專案裡先跑它自己的檢查：`uv run roy-editor youtube preflight`
2. `upload/run_ep.sh NN --dry-run`  
   它讀收件匣的 `meta.json`，呼叫上傳程式，並加上 `--lang zh-TW --synthetic yes`。
3. 標題、標籤或說明裡若有學校名稱，腳本結束碼是 3，不會上傳。這段檢查只寫在 `upload/run_ep.sh`。
4. `upload/do_ep.sh NN` 會先 dry-run。輸出裡要有 `"dry_run"`（或已經傳過的 `"already_uploaded"`），才會真的傳。成功且狀態是 `"uploaded"` 之後，刪掉收件匣裡的 mp4。
5. `upload/record.py EP 標題 影片ID uploaded` 會把一筆紀錄加進 `youtube_uploads.json`。

上傳程式印出的 JSON 會用到 `status`、`url`、`metadata.title`。

## 公開倉庫裡的影片 ID

這個 GitHub 倉庫是公開的，24 筆上傳紀錄裡的私人影片 ID 已改成 `REDACTED-EP00` 這種佔位符，網址也是 `https://youtu.be/REDACTED-EP00`，打不開那支片。真實 ID 留在上傳那台電腦的紀錄裡，不要貼回 git。

`machine` 欄位是 `<mac-hostname>`。進度檔裡的雲端硬碟連結是 `<drive-link-redacted>`。

## 播放清單

上傳完成後，打開 YouTube Studio，把私人影片排進「機器學習從零開始」的播放清單。順序是 EP00、EP01、…、EP20，然後實戰 A1、A2 上、A2 下。API 權限不夠做這件事，不要寫一支「自動排清單」的程式去擴權，除非你另外申請了清單的權限並把它放在這台公開倉庫外面。

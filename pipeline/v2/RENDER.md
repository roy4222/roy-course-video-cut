# 怎麼算一集

下面是 2026-10-31 實際在跑的步驟。機器編號、區網位址、家目錄都不寫在這裡。每台電腦把自己的路徑寫進 `config.env`，見 [config.example.env](config.example.env)。

金鑰只有一個名字：`OPENROUTER_API_KEY`。放在桌機那份套件的 `.env`。不要複製、不要印出來、不要寫進 `config.env`。Mac mini 和 box 的 `.env` 維持佔位符，它們不配音。

## 機器角色

| 角色 | 做什麼 | 編碼 |
|---|---|---|
| 桌機 | 唯一配音的機器。也負責 NVENC 算圖 | `--nvenc`，Whisper 可以用 CUDA |
| Mac mini | CPU 算圖。大約 9 分鐘一集（`--workers 3`） | CPU |
| box | 腳本、轉 `build.py`、QC、共用 `$SEC_SERIES`。大約 18 分鐘一集（`--workers 5`）。記憶體大約 16GB，Chromium 容易被系統殺掉 | CPU |
| MacBook | 只上傳私人 YouTube。不要跑配音、Whisper 或算圖，它會過熱 | 不用 |

三台算圖機器上的套件都加過圖片元素（截圖、錄屏的影格序列；旁白比片段長的時候，停在最後一格）。那個修補檔沒有在這次匯出裡，v1 的 `windows-kit/engine/engine.js` 目前沒有 `R.img`。`build.py` 會寫出 `E('img', ...)`。套件還沒有這個元素之前，截圖和錄屏不會畫出來。見下面「這次匯出沒有的檔」。

## 1. script.md 轉成 build.py（box）

```bash
cd "$SEC_SERIES"
python3 /path/to/roy-course-video-cut/pipeline/v2/tools/md2build_v2.py ep11 ep12
# 寫出 epXX/build.py 和 epXX/film_media/{img,rec}
# 錄影抽成 5fps、寬 1600 的 JPEG；截圖進 img/，角標來自 .credit.txt
# 接著會自動跑 trim_dark_tail.py，裁掉錄屏頭尾的黑幀

tar -czf "epXX_media.tgz" -C epXX film_media build.py
tar -czf "xfer/tts_XX.tgz" epXX/build.py epXX/meta.json
```

集數可以是 `03b` 這種形式。腳本在這個倉庫的 `pipeline/v2/tools/`，不在 `windows-kit` 裡面。`$KIT` 只負責算圖。

## 2. 配音（只有桌機）

把很小的 `tts_XX.tgz` 放到桌機的 `$SEC_INBOX`，然後在 PowerShell：

```powershell
$ep = Join-Path $env:KIT "episodes\secXX"
New-Item -ItemType Directory -Force -Path (Join-Path $ep "film") | Out-Null
# 解開 tarball，把 build.py、meta.json 放進 $ep
$env:PYTHONIOENCODING = 'utf-8'
Set-Location $env:KIT
& "$env:KIT\.venv\Scripts\python.exe" make_episode.py $ep build tts
```

一集大約 6–9 分鐘。多集一起配音可以。紀錄出現 `ALL DONE` 就結束。改過的句子才會重錄。

給另一台機器的配音包：

```powershell
Set-Location $ep
tar -czf (Join-Path $env:SEC_INBOX "secXX_voice.tgz") voice script.json scenes.json meta.json
Get-FileHash (Join-Path $env:SEC_INBOX "secXX_voice.tgz") -Algorithm SHA256
```

## 3. 搬檔

兩邊都對 SHA256。大檔一次只傳一條。桌機同時開兩條傳輸時，會變得暫時連不上。

- 單次大約 40MB 以內可以直接傳。
- 更大的檔切成大約 18–30MB，傳完再接起來（Windows：`copy /b`，macOS／Linux：`cat`）。
- 桌機送到 mini 時，若 mini 有開一個只在區網收檔的位址，用 `SEC_INBOX_URL`。不要把真實 IP 寫進 git。

## 4. 算圖

需要這些東西都在集數目錄裡：`voice/`、`script.json`、`scenes.json`、`meta.json`、`build.py`、`film/img`、`film/rec`。

算之前確認兩件事：

- `build.py` 裡每一個 `src='img/...'` 和 `dir='rec/...'` 在 `film/` 下面都找得到檔案。
- 素材檔名是 ASCII。

Mac mini 或 box（CPU）：

```bash
# 變數見 config.env。NN 是集數，例如 11 或 03b 裡的數字部分依你的目錄為準。
E="$KIT/episodes/secNN"
mkdir -p "$E/film"
tar -xzf "$SEC_INBOX/secNN_voice.tgz" -C "$E"
tar -xzf "/tmp/epNN_media.tgz" -C /tmp/mNN
cp -R /tmp/mNN/film_media/. "$E/film/"
cp /tmp/mNN/build.py "$E/"
cd "$KIT"
nohup .venv/bin/python make_episode.py "episodes/secNN" \
  build timeline layout render mix mux master srt md qc yt \
  --workers 3 --whisper-device cpu \
  > "episodes/secNN/pipe_sec.log" 2>&1 &
```

box 上也可以用 `pipeline/v2/align_qc/r2run_box.sh`。它會先做時間軸，再用 `r2_align.py` 對真實配音做逐句對齊，然後才渲染。

桌機（GPU）：

```powershell
$env:KIT_NVENC = '1'
& "$env:KIT\.venv\Scripts\python.exe" make_episode.py $ep timeline layout render mix mux master srt md qc yt --nvenc --workers 6
```

有 NVENC 的時候一次只渲染一集。消費級驅動的工作階段有上限。

字幕：燒進畫面的字在時間軸那一步就定了。逐句對齊用 `align_qc/r2_align.py`（真實的每一句 wav，每個 cue 最多 18 字，而且不會寫出倒置或長度為零的 cue）。不要把英文單字切開的切法在 `align_qc/r2_align_v2.py` 的 `chunk_v2`。

## 5. 壓小（Drive 單檔上限 100MB）

CPU：

```bash
ffmpeg -i epXX.mp4 -c:v libx264 -preset faster -crf 27 -maxrate 850k -bufsize 1700k \
  -c:a aac -b:a 96k -movflags +faststart SECXX.mp4
```

大約 13 分鐘、40–45MB。桌機可以用 NVENC，目標碼率大約 650k。

## 6. QC

不過關就不要上傳。

| 閘門 | 怎麼看 |
|---|---|
| 同步相似度 | `qc/sync.json` 或 `r2_qc2.py` 的結果。逐 cue 的相似度平均要過得去（大約 0.8 以上當參考），`|start_offset| ≥ 0.9` 秒的句子要點開聽 |
| `over18 = 0` | 沒有超過 18 字的 cue。單一程式識別字比 18 字還長時，整詞自成一個 cue，不要從中間切開，並在表上註明 |
| 沒有缺 cue | 對齊後的文字（去掉標點）和旁白逐字相同 |
| 沒有倒置 cue | 沒有結束早於開始、長度為零、或互相重疊的 cue |
| 沒有別人的視窗 | 六張抽幀，以及每個錄屏場景的開頭約 3 秒、中間、結尾。終端機裡不能出現另一個工作階段的視窗 |
| 沒有黑畫面 | `blackdetect` 是 0。錄屏場景的最後一幀不能停在全黑 |
| 片長 | 10–15 分鐘 |

抽幀：在大約 5%、20%、40%、60%、80%、95% 各拿一張，拼成一張總表看過。`r2_finish.sh` 會做這張總表。`recframes.py` 會再對每個錄屏場景抽開頭、中間、結尾。

成品目錄 `$SEC_SERIES/out/SECXX/`：`SECXX.mp4`、`SECXX.srt`、`thumb.jpg`（第 4 秒附近、寬 1280）、`youtube.json`、`qc/`。`r2_pack.py` 組 `youtube.json` 時會把磁碟路徑和 `sk-or-` 開頭的字串清掉，清不乾淨就拒絕寫出。

## 7. 上傳

1. 上傳到 Drive 資料夾「教學影片／系統與軟體安全」。連結在倉庫根目錄的 [COURSES.md](../../COURSES.md)。放 mp4、srt、`youtube.json`、縮圖。不要從這一步直接上 YouTube。
2. 再到 MacBook，把成片以**私人**影片上傳。上傳程式不在這個倉庫。它不能建播放清單，也不能加字幕軌。播放清單和可開關的字幕軌要另外在 YouTube Studio 處理。
3. 換掉已經上傳的版本之前，先問 Boss。不要自己刪 Drive 或 YouTube 上的舊檔。

## 這輪修過的三件事

1. **錄屏頭尾的黑幀。** 終端錄影常常開頭大約 3 幀、結尾 1–3 幀是黑的。畫面引擎會停在最後一幀，結果就停在全黑。`tools/trim_dark_tail.py` 會裁掉頭尾、重新編號，並改 `build.py` 裡的 `n=`。`md2build_v2.py` 轉檔之後會自己跑它。裁過之後若媒體包是舊的，要重新打包，讓影格和 `build.py` 一致。
2. **檔名只用 ASCII。** 例如帶中文的 png 傳到桌機後會變成空畫面。渲染前對一下 `build.py` 點到的每個檔都在 `film/` 裡。
3. **字幕不要切壞。** 以 token 切：英文字、程式識別字、檔名、路徑不切開；數字和單位（萬、億、%、美元）不切開；只有標點的 cue 丟掉；一個字的尾巴併回上一個 cue。每個 cue 最多 18 字。單一識別字超過 18 字時整詞保留。現行程式是 `r2_align.py`（含倒置 cue 的修正）和 `r2_align_v2.py`。

## 這次匯出沒有的檔

當天機器上有、這個壓縮檔裡沒有的東西，不要當成已經在倉庫裡：

| 檔 | 做過什麼 |
|---|---|
| 圖片元素修補（當天叫 engine image patch） | 在畫面引擎加 `R.img`：一張圖，或一串影格。旁白比較長就停在最後一格。v1 的 `engine.js` 還沒有這個元素 |
| 套件裡 `force_srt.py` 的切字修補 | 和 `chunk_v2` 同一套規則，燒錄字幕在時間軸那一步就會用到。規則的可執行版本在 `align_qc/r2_align_v2.py` |
| `trim_dark_tail.py` | 匯出裡只有呼叫，沒有腳本。倉庫裡這份是照當時的筆記補上的：裁頭尾近黑的 JPEG、重新編號、改 `n=` |

`build_plan.py` 的匯出在第 10 集的字串中間斷掉，倉庫裡只留完整的第 1–9 集。全季大綱看 [COURSES.md](../../COURSES.md) 的課程計畫頁。

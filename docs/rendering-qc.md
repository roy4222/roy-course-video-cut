# 渲染與品質檢查

渲染把 `film/index.html` 畫成無聲的 mp4，再和旁白接在一起。字幕已經畫在 canvas 上。

## 誰在畫

`render/video.mjs` 開 N 個無頭 Chromium。每個工人用 JPEG 截圖，用管線送給自己的 ffmpeg，畫完整段後再無損接起來。預設每秒 30 張。

工人數預設是 `min(8, CPU 執行緒÷4, 記憶體 GB÷6)`。參考機（24 執行緒、48 GB）會得到 6。每個工人大約再吃 1–1.5 GB 記憶體。

指令列 `--workers N` 或環境變數 `KIT_WORKERS` 可以改。`--nvenc` 時中間片段和成片改用 `h264_nvenc`（`-preset p6` 這類設定在 `make_episode.py` 的 mux；片段編碼在 `video.mjs`）。沒有 NVENC 就用 `libx264`，成片是 `-preset slow -crf 19`。

`--low-priority` 會把這個行程的優先權降低，邊做片還能用電腦。

## 機器不夠時

當天的紀錄裡，8 核心、大約 15 GB 記憶體的機器同時渲染，會出現：

`page.screenshot: Timeout 30000ms exceeded`

那台機器上，**整台同時只開到 2 個渲染工人**。舊的 D 管線會先看有沒有別的 `image2pipe`，以及可用記憶體是不是連續兩次檢查都多於約 3.5 GB。

有 NVIDIA 消費級顯示卡時，驅動能同時開的 NVENC 工作階段有上限（新驅動大約 8，舊的大約 3–5）。桌機（RTX 3060 Ti）因此**一次只渲染一集**。`windows-kit/queue1.ps1`、`queue2.ps1`、`queue3.ps1` 就是在等上一集的 `EXIT` 再跑下一集。`--nvenc` 若失敗，把 `--workers` 降到 5 以下，或拿掉 `--nvenc`。

畫面上的格子和卡片是 canvas 2D，不需要 WebGL。軟體 WebGL（llvmpipe）的警告可以忽略。

Windows 若成片正開在播放器裡，覆寫會 `PermissionError`。關掉播放器再跑。上次渲染當掉可能留下 `out/video.mp4.lock`，確認沒有渲染在跑之後刪掉它。

## 聲音與響度

1. `mix`：每句 wav 放在時間軸的 t0，寫出 `out/mix.wav`。
2. 限幅：`alimiter=limit=0.5:attack=5:release=50:level=disabled` → `out/mix_lim.wav`。這一步是為了 Gemini 峰值偏高，不要跳過。
3. `mux`：兩段式 `loudnorm=I=-14:TP=-1.2:LRA=11`（先量、再套用量到的值，`linear=true`）。影像 `fps=30,format=yuv420p`，AAC 256k，faststart。若綜合響度不在 −15 到 −13，或真峰值高過 −1 dBTP，紀錄會警告。
4. `master`：`volume=0.35dB`，升到 96 kHz 再限幅 `limit=0.8`，回到 48 kHz，AAC 192k，影像直接複製。量測寫進 `qc/loudness.json`。

當天有幾集 mux 沒有剛好落在 −14（例如警告寫 missed -14 LUFS）。**`master` 就是在補這一步。** 不要在 mux 警告之後就停。當天最終大約是 −13.7 到 −14.1 LUFS，真峰值大約 −1.2 到 −1.6 dBTP。

## 品質檢查在看什麼

`layout`（警告而已）：

- OUT-OF-FRAME：文字框 x<20、x>1900 或 y>1075
- OVERLAP：兩個文字框重疊超過較小那個的 15%
- UNDER-SUBTITLE：內容的底邊掉進字幕區

`qc`：

- 在片長的 3%、15%、28%、40%、52%、64%、77%、90% 各抓一張圖到 `qc/f*.jpg`
- 用 Whisper small 聽大約在 20%、50%、80% 的三句（前後各留約 1 秒），比對字幕文字，並看開始時間差多少，寫進 `qc/sync.json`

`legacy/qc/final_qc.py` 是事後再查一次：是不是 1080p、30 fps、響度、片長對不對最後一條字幕、以及幾條字幕開始時音量有沒有起來。套件的 `qc` 步驟沒有把這個檔接進去。你要對成片再查一次時，手動跑它（它讀 `VIDEO_STYLE_ROOT` 底下的 `epNN/epNN.mp4`）。

## 出片前清單

- [ ] `build.py` 跑完沒有「句子編號不存在」
- [ ] `qc/layout.txt` 沒有你不能接受的重疊或出界（警告不會自己停）
- [ ] 抽聽開頭、中間、結尾。Whisper 的同音字（信／性、序章／續章）用耳朵判斷
- [ ] `qc/sync.json` 的相符度不要只靠一個很低的數字就重錄整集，先聽那一句
- [ ] `pipe.log` 的 `[mux]`、`[master]` 看過；`qc/loudness.json` 大約在 −14 LUFS，真峰值不高過 −1 dBTP
- [ ] `epNN.srt` 跟畫面字幕是同一句話
- [ ] `youtube.json` 沒有本機路徑、沒有長串亂碼、沒有 `sk-or-`
- [ ] 標題、標籤、說明沒有學校名稱
- [ ] 播放器裡沒有開著舊的 mp4（Windows 會鎖檔）

寫畫面、還不想花錢配音時：

```text
make_episode.cmd <集數資料夾> build timeline stills
```

改了字或 `say` 之後再跑全流程，只有雜湊變了的句子會重錄。

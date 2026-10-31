# 系統與軟體安全 · 交接（2026-10-31 14:00，台北時間）

對象是 Boss（Roy）。旁白和說明用繁體中文。這門課從零基礎開始，接到公開課 CS161、CS155、6.566 的作業。貫穿的例子是導盲機器狗（FenrisOS、Unitree Go2）。逆向那集用公開的 go2_ros2_sdk（SEC03b）。台灣薪資的數字用 104。

機器編號、區網位址、家目錄、上傳憑證都不寫在這份文件裡。路徑見 [config.example.env](config.example.env)。

## 要守住的偏好

- 正集 SEC00–39，加碼 HX。每一集 10–15 分鐘，理想 12–14 分鐘，交接時的目標區間寫的是 10–13 分鐘。
- 鉤子穿在每一段裡（真實案例、馬上可以試、停下來猜），不只開場。大約最多 3 分鐘一個。
- 要真的工具錄屏、真的截圖和投影片、圖解。不要只有表格。
- 字幕必須對上真實的配音。這是最在意的一點。不可以太快。每個 cue 最多 18 字。不切開英文字，不切開數字和單位，沒有單獨一個字或單獨一個標點的 cue。
- 風格對齊技術解說片和 lemo-opuscar 那種畫面：內容要準、好吸收、畫面要換。
- 可以直接做，用產線並行。2026-10-31 12:27 Boss 說先慢下來，一次一兩台。
- MacBook 會過熱。配音和算圖不要放上去。它只負責私人 YouTube 上傳。

## 機器角色

| 角色 | 做什麼 |
|---|---|
| MacBook | 只上傳私人影片。不要讀、不要複製上傳憑證。權限不夠建播放清單，也不夠加字幕軌 |
| Mac mini | CPU 算圖。入口是 `align_qc/r2run_box.sh` 那一類腳本，工人數大約 3 |
| 桌機 | NVENC。Whisper 可以用 CUDA。金鑰只在這台的套件 `.env`，變數名稱 `OPENROUTER_API_KEY` |
| box | `$SEC_SERIES` 的共用檔案。記憶體大約 16GB，Chromium 算圖可能被系統殺掉 |

## 產線

- 配音：OpenRouter `google/gemini-3.8-flash-tts`，聲音 Enceladus。
- 字幕：`align_qc/r2_align.py` 已修，不會寫出倒置或長度為零的 cue。`align_qc/r2_align_v2.py` 不切開英文和數字單位，也沒有單字 cue。
- QC：同步相似度、聽得見、`over18 = 0`、沒有缺 cue、沒有倒置 cue、沒有別人的視窗、沒有黑畫面、10–15 分。
- 輸出：mp4（小於 100MB）、srt、縮圖、`youtube.json`，先到 Drive。大檔在區網傳，兩邊對 SHA256。一次只傳一條。
- 協調：`$SEC_SERIES/STATUS.md` 先認領再做。每一集目錄的空檔 `READY`。錄屏的 X 畫面分段，避免撞到別人的視窗。素材檔名必須是 ASCII。

同一套說明還有 [FORMAT.md](FORMAT.md)、[RENDER.md](RENDER.md)、[REVIEW.md](REVIEW.md)、[STATUS.md](STATUS.md)。

## 進度（14:00）

- 課程計畫頁和播放清單、Drive、26 支私人影片的連結在倉庫根目錄 [COURSES.md](../../COURSES.md)。
- 腳本：SEC00–39 都已 READY（多數有 v2 加強版）。HX01–10 都寫好了。
- 已算完、QC 通過、在 Drive、已上 YouTube（私人）共 26 部：SEC00（v2）、01–13、03b、16–20、22、23、26、28、29、HX10。
- 還沒做完的：
  - SEC14、SEC21：算過了，但有一段字幕慢 2–4 秒。用逐字時間戳改 `cues_fine.json` 和 `film/timeline.js`，再在 Mac mini 重跑該集的算圖步驟。
  - SEC15：算過了，還沒 QC。
  - SEC24：QC 失敗（倒置 cue）。cue 已手改，需要重算。
  - SEC25、27、31：配音在 box 的收件目錄，還沒算。SEC32–36：配音在桌機的套件集數目錄，還沒算。SEC30、37–39：還沒算。
  - HX01–09：腳本和錄屏完成，還沒算。
  - SEC01–10 的 v2 重算（新字幕已在 Drive；SEC01、05、08 的 v2 `build.py` 修了停很久的截圖；SEC09、17 的中段鉤子要補配音）。v2 上傳之後再換播放清單裡的舊版。刪舊檔之前必須問 Boss。
  - 可開關的 YouTube 字幕軌還沒上。SEC00–10 和 03b 用 v2 的 srt。
  - SEC10（9:49）、SEC22（8:44）、SEC23（8:56）偏短。SEC22 大約 2:34 附近有 4 句字幕慢約 2.5 秒。

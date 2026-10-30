# 配音與對齊

配音走 OpenRouter 的語音 API。金鑰是環境變數 `OPENROUTER_API_KEY`，放在 `windows-kit/.env`。程式只把它放進 `Authorization` 標頭，不會印出來，也不會寫進 `youtube.json`。

## 請求

- 網址：`POST https://openrouter.ai/api/v1/audio/speech`
- 模型：`google/gemini-3.8-flash-tts`（`KIT_TTS_MODEL` 可改）
- 聲音：`Enceladus`（`KIT_TTS_VOICE` 可改）
- `response_format`: `pcm`
- 提示句：台灣華語、對完全新手說話的老師、不趕（見 `kit/tts_openrouter.py`）
- ffmpeg 把 s16le PCM 轉成 24 kHz 單聲道 wav

一集的句子會依場景分成幾段，**一段最多大約 380 個字**，一段一個請求。一段裡的句子用換行接在一起，所以語氣比較連貫，請求次數也少。一集大約 15 個請求。

費用從回應標頭的 `X-Generation-Id` 再查 `GET /api/v1/generation?id=...`，記在 `voice/costs.json`。每句長度記在 `voice/dur.json`。

`voice/manifest.json` 用「模型 + 聲音 + 提示 + 句子」的雜湊記住這句已經錄過。句子沒改就不會重錄，也不會再花錢。

## 一段音怎麼切回每一句

`make_episode.py` 的 `tts` 步驟對每一段這樣做：

1. **停頓切**（`kit/sil_split.py`）。不跑語音辨識，快。有信心就採用。
2. 信心不夠就用 **faster-whisper**（模型 `small`）的逐字時間去對句子（`kit/whisper_align.py`）。每一句的相符度都至少 0.5 才採用。
3. 還是不行，就把這段音標成低信心，**整段重錄一次**，再走 1 和 2。
4. 仍然不行，就**每一句各發一個請求**（比較貴，也比較穩）。

只想走第 4 步：`--tts-mode line`。EP17 最後就是這樣做完的，桌機上的指令留在 `windows-kit/run_ep17_tts.cmd`。

CUDA 可用時加 `--whisper-device cuda`（要先 `setup -Cuda`）。載入失敗會退回 CPU。

## 常常遇到的事

**HTTP 429。** 上游會限流。`tts_openrouter.py` 會等了再試，最多大約 12 次，等待從 5 秒倍增到 90 秒。舊的 `pipe.py` 外面還有一層更長的等待。中斷了再跑同一個指令即可，錄好的句子不會重來。一集如果一直 429，把場景音先備好可以藏住等待（舊工具的 `legacy/pipeline_D/prefetch.py` 就是在做這件事；套件本身是錄一段、切一段）。

**讀取逾時。** `The read operation timed out` 會被當成可重試的錯誤。

**切句失敗。** 紀錄裡出現過 `alignment failed between line 0 and 1`，以及空序列的 `argmin`。多半是很短的開場、測驗、標題卡。讓它落到逐句重錄，或對那一集改用 `--tts-mode line`。

**Whisper 把同音字聽錯。** 品質檢查裡「信」會被聽成「性」、「序章」會被聽成「續章」。那是辨識的錯，不是配音念錯。用耳朵確認。相符度當天大約在 0.78 到 0.96，C 那幾集較低。

**峰值很大聲。** Gemini 的音檔峰值偏高。混音之後、接上畫面之前一定要過限幅器。這一步在 `mix`，不要拿掉。細節在 [渲染與品質檢查](rendering-qc.md)。

**`av` 19。** `av` 19 會讓 faster-whisper 1.2 丟出 `TypeError: metadata_errors`。`requirements.txt` 寫 `av>=12,<19`。升級時不要放掉這個上限。

## 別的聲音

當天試過別的模型和 edge-tts 的 `zh-TW-HsiaoChenNeural`，最後指定 Enceladus。試聽程式在 `legacy/tools/voice_test/`。edge-tts 是 lemo-opuscar 裡的 `core/tts/tts_zh.py`，套件的預設路徑沒有改走它。要換聲音，先改 `.env` 的 `KIT_TTS_VOICE`，用很短的句子試聽，再決定要不要整集重錄。

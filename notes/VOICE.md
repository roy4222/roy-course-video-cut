# 配音預設（2026-10-30 Boss 指定）

- 預設聲音：OpenRouter `google/gemini-3.8-flash-tts`，voice **Enceladus**
- instructions：Speak in Mandarin Chinese with a Taiwan Mandarin accent (台灣國語口音), like a warm, clear, friendly teacher explaining to a complete beginner, at a moderate, unhurried pace.
- 工具：`/workspace/venv/bin/python lemo-opuscar/core/tts/tts_openrouter.py lines.json voice_dir`（預設 --mode scene：每個場景一次請求，再用 faster-whisper 對齊切回每一句；輸出 <id>.wav + dur.json + costs.json，與 tts_zh.py 相同介面）
- 金鑰：環境變數 OPENROUTER_API_KEY（不要印出）
- 注意：上游常回 HTTP 429，工具會自動退避重試；一集約需 15 次請求。
- 備援：edge-tts zh-TW-HsiaoChenNeural（`core/tts/tts_zh.py --voice zh-TW-HsiaoChenNeural --rate +0%`）
- 混音：Gemini 音檔峰值偏高，mux 前先過限幅器再交給 mux.sh：
  `ffmpeg -i mix.wav -af "alimiter=limit=0.5:attack=5:release=50:level=disabled" mix_lim.wav`（EP01 實測 −14.0 LUFS、峰值 −1.2 dBFS）
- 依賴：faster-whisper、opencc-python-reimplemented、soundfile（/workspace/venv 已裝）。請用 /workspace/venv/bin/python 執行 tts_openrouter.py。
- 已知小問題：Whisper 反聽會把「信」聽成「性」、「序章」聽成「續章」，屬同音誤判，人耳確認即可。

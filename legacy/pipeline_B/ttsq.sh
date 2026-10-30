#!/bin/bash
# sequential TTS queue: reads episode list from ttsq.txt, runs tts for each not yet done
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
while true; do
  next=""
  for e in $(cat epB_engine/ttsq.txt); do
    if [ ! -f $e/voice/dur.json ] && [ -f $e/script.json ]; then next=$e; break; fi
  done
  [ -z "$next" ] && { sleep 60; [ -f epB_engine/ttsq.stop ] && exit 0; continue; }
  pgrep -f "pipe.py . tts" >/dev/null && { sleep 30; continue; }
  (cd $next && "$PY" ../epB_engine/pipe.py . tts >> tts.out 2>&1)
done

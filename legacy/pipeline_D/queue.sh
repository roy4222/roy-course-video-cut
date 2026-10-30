#!/bin/bash
# epD queue: TTS/alignment sequentially (ep18->ep20), post (render WK=2 ... yt) sequentially as each finishes.
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
tts_loop(){ for e in ep18 ep19 ep20; do
  while pgrep -f "epD_engine/pipe.py . tts" >/dev/null; do sleep 20; done
  [ -f $VS/$e/voice/dur.json ] && continue
  (cd $VS/$e && $PY ../epD_engine/pipe.py . tts >> tts.out 2>&1); done; }
post_loop(){ for e in ep18 ep19 ep20; do
  n=${e#ep}; while [ ! -f $VS/$e/voice/dur.json ]; do sleep 30; done
  [ -f $VS/$e/$e.mp4 ] && continue
  (cd $VS/$e && WK=2 $PY ../epD_engine/pipe.py . timeline layout render mix srt md qc yt >> post.out 2>&1) || touch $VS/$e/.postfail; done; }
tts_loop & post_loop & wait
echo QUEUE DONE

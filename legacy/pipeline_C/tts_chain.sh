#!/bin/sh
# usage: tts_chain.sh WAITPID ep ep ...
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
W=$1; shift
while kill -0 $W 2>/dev/null; do sleep 15; done
for ep in "$@"; do
  "$PY" -c "import json,sys;P=json.load(open('progress_C.json'));sys.exit(0 if P.get('$ep',{}).get('tts') else 1)" && continue
  "$PY" common_C/make_ep_c.py $ep script >> ep$ep/tts.log 2>&1
  "$PY" common_C/make_ep_c.py $ep tts >> ep$ep/tts.log 2>&1 || echo "TTS FAIL $ep" >> common_C/queue.log
  echo "tts $ep $(date +%H:%M)" >> common_C/queue.log
done

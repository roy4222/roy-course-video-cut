#!/bin/sh
# sequential TTS for my episodes (waits for src.py)
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
for ep in ${EPS:-00 02 03 04 05 06 07 08 09 10}; do
  while [ ! -f ep$ep/src.ready ]; do sleep 30; done
  "$PY" common/make_ep.py $ep script && "$PY" - "$ep" <<'P' || "$PY" common/make_ep.py $ep tts
import json,sys; P=json.load(open('progress_A.json')); sys.exit(0 if P.get(sys.argv[1],{}).get('tts') else 1)
P
done
echo ALL_TTS_DONE

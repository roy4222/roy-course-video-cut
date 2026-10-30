#!/bin/sh
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
for ep in ${EPS:-06 07 08 09 10}; do
  until "$PY" -c "import json,sys;P=json.load(open('progress_C.json'));sys.exit(0 if P.get('$ep',{}).get('tts') else 1)" 2>/dev/null; do sleep 30; done
  WORKERS=2 "$PY" common_C/make_ep_c.py $ep all >> ep$ep/build.log 2>&1 || echo "BUILD FAIL $ep" >> common_C/queue.log
  echo "built $ep $(date +%H:%M)" >> common_C/queue.log
done
echo ALL_BUILT >> common_C/queue.log

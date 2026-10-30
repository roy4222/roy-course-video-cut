#!/bin/sh
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
for ep in ${EPS:-02 03 04 05}; do
  until "$PY" -c "import json,sys; P=json.load(open('progress_A.json')); sys.exit(0 if P.get('$ep',{}).get('tts') else 1)" 2>/dev/null; do sleep 30; done
  WORKERS=${WORKERS:-4} "$PY" common/make_ep.py $ep all > ep$ep/build.log 2>&1 || echo "FAIL $ep"
  echo "built $ep $(date +%H:%M)"
done
echo ALL_BUILT

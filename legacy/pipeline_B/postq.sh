#!/bin/bash
# after TTS: post steps sequential (one episode at a time => never two of my renders); WK=1 (2 only if no other render & >6GB free)
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
cd "$VS"
while true; do
  did=0
  for e in $(cat epB_engine/ttsq.txt); do
    n=${e#ep}
    if [ -f $e/voice/dur.json ] && [ ! -f $e/ep$n.mp4 ] && [ ! -f $e/.postfail ]; then
      while pgrep -f "video.mjs ${VS}/ep1[1-7]/film" >/dev/null; do sleep 30; done
      avail=$(free -g | awk '/Mem:/{print $7}')
      if ! pgrep -f image2pipe >/dev/null && [ "$avail" -gt 6 ]; then export WK=2; else export WK=1; fi
      echo "$(date +%T) start post $e WK=$WK" >> epB_engine/postq.log
      (cd $e && "$PY" ../epB_engine/pipe.py . timeline layout render mix srt md qc yt >> post.out 2>&1) || touch $e/.postfail
      did=1; break
    fi
  done
  [ $did = 0 ] && { [ -f epB_engine/postq.stop ] && exit 0; sleep 60; }
done

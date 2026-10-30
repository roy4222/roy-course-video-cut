#!/bin/bash
VS="${VIDEO_STYLE_ROOT:-/workspace/video_style}"
PY="${VIDEO_STYLE_PYTHON:-/workspace/venv/bin/python}"
for e in ep19 ep20; do
  [ -f $VS/$e/$e.mp4 ] && continue
  (cd $VS/$e && WK=1 $PY ../epD_engine/pipe.py . timeline layout render mix master srt md qc yt >> post.out 2>&1) || touch $VS/$e/.postfail
done; echo POST2 DONE

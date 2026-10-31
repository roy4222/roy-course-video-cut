#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# rec30.sh N scene.sh out_base  — record on :18N (181-189 only) with ffmpeg + asciinema .cast
N=$1; D=18$N; case $D in 18[1-9]) ;; *) echo "display must be :181-:189"; exit 1;; esac
SCENE=$(readlink -f $2); OUT=$3; export DISPLAY=:$D
Xvfb :$D -screen 0 1920x1080x24 -ac >/dev/null 2>&1 & XV=$!; sleep 1.5
xsetroot -solid "#0d1117" 2>/dev/null
ffmpeg -y -loglevel error -f x11grab -video_size 1920x1080 -framerate 30 -i :$D -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$OUT.mp4" &
FF=$!; sleep 0.5; xdotool mousemove 1919 1079
xterm -geometry 118x33+0+0 -fa 'DejaVu Sans Mono' -fs 19 -xrm 'XTerm*faceNameDoublesize: Noto Sans Mono CJK TC' -bg '#0d1117' -fg '#e6edf3' -b 20 -xrm 'XTerm*cursorColor: #58a6ff' -e asciinema rec -q --overwrite -c "bash -c 'cd $SEC_LAB; source $REC_DIR/typer.sh; source ~/.bashrc; clear; source $SCENE; sleep 2.5'" "$OUT.cast"
kill -INT $FF; wait $FF 2>/dev/null; kill $XV
echo "recorded $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT.mp4)s"

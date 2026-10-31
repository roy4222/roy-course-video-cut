#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
D=${D:?set D=91..99}; case $D in 9[1-9]) ;; *) echo "display must be :91-:99"; exit 1;; esac
# record.sh scene.sh out.mp4  — run scene in xterm on :${D}, capture with ffmpeg
SCENE=$(readlink -f $1); OUT=$2; export DISPLAY=:$D
ffmpeg -y -loglevel error -f x11grab -video_size 1920x1080 -framerate 30 -i :${D} -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$OUT" &
FF=$!; sleep 0.5; xdotool mousemove 1919 1079
xterm -geometry 118x33+0+0 -fa 'DejaVu Sans Mono' -fs 19 -xrm 'XTerm*faceNameDoublesize: Noto Sans Mono CJK TC' -bg '#0d1117' -fg '#e6edf3' -b 20 -xrm 'XTerm*cursorColor: #58a6ff' -e bash -c "cd ${WD:-$SEC_LAB}; source $REC_DIR/typer.sh; source ~/.bashrc; export GHIDRA_INSTALL_DIR=$GHIDRA_INSTALL_DIR; clear; source $(readlink -f $SCENE); sleep 2.5"
kill -INT $FF; wait $FF 2>/dev/null
echo "recorded $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT)s"

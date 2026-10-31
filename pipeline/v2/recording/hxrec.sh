#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# hxrec.sh N scene.sh out.mp4 workdir — 只用 Xvfb :171–:179；同時錄 .cast（asciinema）與 .mp4（ffmpeg x11grab）
N=$1; SCENE=$(readlink -f $2); OUT=$(readlink -f $3); WD=$4; CAST="${OUT%.mp4}.cast"
[[ $N -ge 171 && $N -le 179 ]] || { echo "display must be 171-179"; exit 1; }
export DISPLAY=:$N
pkill -f "Xvfb :$N " 2>/dev/null; sleep 0.3
Xvfb :$N -screen 0 1920x1080x24 -nolisten tcp >/dev/null 2>&1 & XP=$!; sleep 1.2
xsetroot -solid "#0d1117"
cat > /tmp/hxinner_$N.sh <<IN
cd $WD; source $REC_DIR/typer.sh; export PSUSER=\${PSUSER:-roy}; clear; source $SCENE; sleep 2
IN
ffmpeg -y -loglevel error -f x11grab -video_size 1920x1080 -framerate 30 -i :$N -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "$OUT" & FF=$!
sleep 0.4; xdotool mousemove 1919 1079
xterm -geometry 118x33+0+0 -fa 'DejaVu Sans Mono' -fs 19 -xrm 'XTerm*faceNameDoublesize: Noto Sans Mono CJK TC' -bg '#0d1117' -fg '#e6edf3' -b 20 -xrm 'XTerm*cursorColor: #58a6ff' \
  -e asciinema rec -q --overwrite --cols 116 --rows 31 -c "bash /tmp/hxinner_$N.sh" "$CAST"
kill -INT $FF; wait $FF 2>/dev/null; kill $XP 2>/dev/null
echo "recorded $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 $OUT)s"

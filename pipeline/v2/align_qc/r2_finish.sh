#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# r2_finish.sh NN box|in   -> $SEC_SERIES/out/SECNN/{SECNN.mp4,SECNN.srt,thumb.jpg,youtube.json,qc/}
N=$1; O=$SEC_SERIES/out/SEC$N; mkdir -p $O/qc
if [ "$2" = box ]; then
  E=$KIT/episodes/sec$((10#$N))
  ( cd $E && cp ep$N.srt cues_fine.json cues.json script.json scenes.json meta.json qc/r2_align_stats.json pipe_r2.log $O/qc/ )
  ffmpeg -loglevel error -y -i $E/ep$N.mp4 -c:v libx264 -preset faster -crf 27 -maxrate 850k -bufsize 1700k -c:a aac -b:a 96k -movflags +faststart $O/SEC$N.mp4
else
  tar xzf $R2/in/SEC${N}_meta.tgz -C $O/qc 2>/dev/null; cp $R2/in/SEC$N.mp4 $O/
fi
cp $O/qc/ep$N.srt $O/SEC$N.srt
cd $O && R2_THREADS=${R2_THREADS:-3} $KIT/.venv/bin/python $R2/r2_qc2.py SEC$N.mp4 qc/cues_fine.json qc/script.json qc/r2_qc2.json 2>&1 | grep -v Warning
python3 $R2/r2_pack.py $O $N
# 6-frame montage
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 SEC$N.mp4); i=0; args=""
for f in 0.05 0.2 0.4 0.6 0.8 0.95; do t=$(python3 -c "print($D*$f)"); ffmpeg -loglevel error -y -ss $t -i SEC$N.mp4 -frames:v 1 -vf scale=640:-2 qc/m$i.jpg; args="$args -i qc/m$i.jpg"; i=$((i+1)); done
ffmpeg -loglevel error -y $args -filter_complex "xstack=inputs=6:layout=0_0|w0_0|w0+w1_0|0_h0|w0_h0|w0+w1_h0" qc/montage.jpg
ls -la $O

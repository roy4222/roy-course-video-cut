#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
n=$1; W=${2:-4}; K=$KIT; E=$K/episodes/sec$n; S=$SEC_SERIES/ep$n
mkdir -p $E/film && cd $E
tar -xzf $R2/in/r2_sec${n}_voice.tgz -C $E
rm -rf $E/film/img $E/film/rec; cp -R $S/film_media/img $S/film_media/rec $E/film/; cp $S/build.py $E/
cd $K; LOG=$E/pipe_r2.log; echo "START $(date '+%F %T')" > $LOG
./make_episode.sh episodes/sec$n build timeline --workers $W >> $LOG 2>&1 || { echo "EXIT fail-timeline" >> $LOG; exit 1; }
KIT=$K R2_THREADS=6 HF_HOME=$K/.cache/huggingface .venv/bin/python $R2/r2_align.py $E >> $LOG 2>&1 || { echo "EXIT fail-align" >> $LOG; exit 1; }
./make_episode.sh episodes/sec$n layout render mix mux master md --workers $W --whisper-device cpu >> $LOG 2>&1
echo "EXIT $? END $(date '+%F %T')" >> $LOG

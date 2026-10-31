#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# render-only (already timeline+aligned) on box: r2render_box.sh NN [workers]
n=$1; W=${2:-3}; K=$KIT; E=$K/episodes/sec$n; LOG=$E/pipe_r2.log
cd $K; echo "RENDER RETRY $(date '+%F %T')" >> $LOG
./make_episode.sh episodes/sec$n layout render mix mux master md --workers $W --whisper-device cpu >> $LOG 2>&1
echo "EXIT $? END $(date '+%F %T')" >> $LOG

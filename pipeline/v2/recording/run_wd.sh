#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# usage: D=94 run_wd.sh EP scene:workdir ...
EP=$1; shift; export PYTHONDONTWRITEBYTECODE=1
for sw in "$@"; do s=${sw%%:*}; export WD=${sw#*:}
  bash $REC_DIR/rec_disp.sh $REC_DIR/s${EP}_$s.sh $SEC_SERIES/ep$EP/recordings/s${EP}_$s.mp4
done; echo ALLDONE

#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# usage: D=91 run1718.sh 17 crash slowmo ...
EP=$1; shift; export PYTHONDONTWRITEBYTECODE=1
export WD=$SEC_LAB/sec$EP
for s in "$@"; do
  bash $REC_DIR/rec_disp.sh $REC_DIR/s${EP}_$s.sh $SEC_SERIES/ep$EP/recordings/s${EP}_$s.mp4
done
echo ALLDONE

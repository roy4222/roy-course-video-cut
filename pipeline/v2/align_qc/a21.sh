#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
K=$KIT; E=$K/episodes/sec21; cd $K
echo "ALIGN RETRY $(date '+%T')" >> $E/pipe_r2.log
KIT=$K R2_THREADS=3 HF_HOME=$K/.cache/huggingface nice -n 19 .venv/bin/python $R2/r2_align.py $E >> $E/pipe_r2.log 2>&1; echo "ALIGN rc=$? $(date '+%T')" >> $E/pipe_r2.log

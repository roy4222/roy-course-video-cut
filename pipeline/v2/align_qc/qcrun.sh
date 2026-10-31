#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# qcrun.sh NN : rerun r2_qc2 (float32) on out/SECNN
cd $SEC_SERIES/out/SEC$1 && R2_THREADS=${R2_THREADS:-3} $KIT/.venv/bin/python $R2/r2_qc2.py SEC$1.mp4 qc/cues_fine.json qc/script.json qc/r2_qc2.json 2>&1 | grep -v Warning | head -n 1

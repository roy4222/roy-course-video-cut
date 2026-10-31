#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export PYTHONDONTWRITEBYTECODE=1 WD=$SEC_LAB/go2re
mkdir -p $SEC_SERIES/ep03b/recordings
for s in tree ids handshake history lidar sdk ghidra; do
  find $WD -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
  bash $REC_DIR/record78.sh $REC_DIR/s03b_$s.sh $SEC_SERIES/ep03b/recordings/s03b_$s.mp4
done
echo ALLDONE

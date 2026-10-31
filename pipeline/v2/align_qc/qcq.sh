#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# qcq.sh : serial QC queue; processes NN listed in qcq.list (one per line) that have in/SECNN.mp4 and no out/SECNN/qc/.qcdone
cd $R2
while true; do
  for n in $(cat qcq.list); do
    O=$SEC_SERIES/out/SEC$n
    [ -f in/SEC$n.mp4 ] && [ ! -f $O/qc/.qcdone ] || continue
    nice -n 15 ./r2_finish.sh $n in > fin$n.out 2>&1; (cd $SEC_SERIES/out && python3 $R2/recframes.py SEC$n $n >> $R2/fin$n.out 2>&1); touch $O/qc/.qcdone
  done
  sleep 15
done

#!/bin/bash
. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
for n in "$@"; do while [ ! -f $R2/in/r2_sec${n}_voice.ok ]; do sleep 10; done; $R2/r2run_box.sh $n 4; done

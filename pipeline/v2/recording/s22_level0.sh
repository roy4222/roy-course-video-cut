. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source $SEC_LAB/sec22/.venv/bin/activate; export PWNLIB_NOTERM=1
say "pwntools-dojo（BSD-2 開源）level 0.0，本機練習版：/flag 改成 ./flag"
runp 'grep -n "flag\"" pwntools-tutorials-level0.0.c' 2
say "先讀題：它要什麼輸入？"
runp 'grep -n -A6 "int bypass_me" pwntools-tutorials-level0.0.c' 3
say "手動亂打一次：失敗"
runp 'echo hello | ./level0.0 | tail -4' 3
say "改用 pwntools：三步——開程式、送字、收結果"
runp 'cat solve0.py' 4
runp 'python solve0.py 2>&1 | grep -v Receiving' 4
say "通關：拿到旗子（本機假旗）"

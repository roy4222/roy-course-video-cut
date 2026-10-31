. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source $SEC_LAB/sec22/.venv/bin/activate; export PWNLIB_NOTERM=1
say "CTF 常給你一個「nc 主機 埠號」。我們在本機開一個一樣的服務"
runp '(python serve.py &) ; sleep 1; ss -ltn | grep 31337' 2.5
say "只聽 127.0.0.1：只有這台電腦自己連得到"
runp 'diff solve0.py remote0.py' 3.5
say "只換一行：process → remote"
runp 'python remote0.py 2>&1 | grep -v Receiving' 4
say "兩行就連上、拿旗。收掉服務"
runp 'pkill -f "python serve.py"; ss -ltn | grep -c 31337' 2

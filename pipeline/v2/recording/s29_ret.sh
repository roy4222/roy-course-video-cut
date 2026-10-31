. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
xt(){ sleep $2; W=$(xdotool search --class xterm|head -1); xdotool windowfocus --sync $W; xdotool type --delay 55 "$1"; xdotool key Return; }
say "先看 ret 這個指令到底做什麼。用上集的 v2_nx（有 NX、有金絲雀）"
runp 'objdump -d -M intel --no-show-raw-insn v2_nx | grep -A5 "fs:0x28" | tail -5' 3
say "最後兩行：leave、ret。停在 ret 那一刻看看"
( xt "break *0x4011a5" 8; xt "run robot" 2.5; xt "x/gx \$rsp" 6; xt "si" 3.5; xt "quit" 5 ) &
runp 'pwndbg -q ./v2_nx' 0.5
wait
say "ret = 從堆疊頂拿一個位址，直接跳過去。它不管那個位址是誰放的"

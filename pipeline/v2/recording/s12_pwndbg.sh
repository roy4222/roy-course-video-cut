. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
export DEBUGINFOD_URLS=
xt(){ sleep $2; W=$(xdotool search --class xterm | head -1); xdotool windowfocus --sync $W 2>/dev/null; xdotool type --delay 55 "$1"; xdotool key Return; }
say "用除錯器 pwndbg 親眼看記憶體被蓋掉（-g 編譯時留下了原始碼對照）"
( xt "break 12" 5; xt "run /cmd_vel_x" 2.5; xt "p c" 6; xt "hexdump &c 12" 3.5; xt "p/x c.estop" 3.5; xt "quit" 5 ) &
runp 'pwndbg -q ./estop' 0.5
wait
say "2f 63 6d 64 ... = /cmd_vel；多出的 5f 78（_x）蓋進了 estop"
say "estop = 0x785f：小端序，低位元組放前面"

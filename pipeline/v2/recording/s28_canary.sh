. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
xt(){ sleep $2; W=$(xdotool search --class xterm | head -1); xdotool windowfocus --sync $W 2>/dev/null; xdotool type --delay 55 "$1"; xdotool key Return; }
say "第一層：Stack Canary（金絲雀）。先看沒有它的版本"
runp 'sed -n "4,8p" guard.c' 3
printf "${PS_COLOR}roy@lab${RST}:\033[1;34m~/lab/mit\033[0m\$ "; type_out './v0_none AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'; sleep 0.4; printf '\n'; sh -c './v0_none AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'; sleep 2.5
say "當掉了，但不知道為什麼。現在換有金絲雀的版本："
runp './v1_canary AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 2>&1 | tail -2' 3
say "程式自己發現：堆疊被踩了，立刻自殺，不讓攻擊者接手"
say "金絲雀長什麼樣？用 pwndbg 看"
( xt "break handle" 8; xt "run AAAA" 2.5; xt "canary" 6; xt "quit" 4 ) &
runp 'pwndbg -q ./v1_canary' 0.5
wait
say "每次執行都換一個隨機值，最低一個 byte 固定是 00"

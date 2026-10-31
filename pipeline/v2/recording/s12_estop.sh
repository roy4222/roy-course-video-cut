. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "越界寫入：topic 只有 8 格，strcpy 不檢查長度"
runp 'sed -n "3,14p" estop.c' 4
runp 'gcc -g -o estop estop.c && ./estop /cmd' 2
say "名字長一點點……"
runp './estop /cmd_vel_x' 2.5
say "剛好 8 個字呢？多出來的那個 \\0 也會寫過界"
runp './estop /cmd_vel' 3
say "差一格（off-by-one），急停旗標就從 1 變 0"

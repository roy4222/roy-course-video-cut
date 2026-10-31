. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "C 的字串 = char 陣列 + 結尾一個看不見的 \\0"
runp 'gcc -o strings strings.c && ./strings' 3
say "strlen 數到 \\0 前為止＝4；實際佔的格子＝5"
say "如果忘了留位置給 \\0 呢？"
runp 'sed -n "3,13p" leak.c' 4
runp 'gcc -o leak leak.c && ./leak' 3.5
say "printf 停不下來，一路讀進隔壁的 token——資料外洩"

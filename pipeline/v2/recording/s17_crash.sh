. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "SEC17 第一個 buffer overflow：自己寫、自己弄壞"
runp 'cat dog_greet.c' 3.5
say "編譯：關掉保護，才看得到原形（只在練習時這樣做）"
runp 'gcc -O0 -g -fno-stack-protector -no-pie -U_FORTIFY_SOURCE -o dog_greet dog_greet.c'
runp './dog_greet Roy'
runp './dog_greet AAAAAAAAAAAAAAA' 2
say "15 個 A：還裝得下（第 16 格留給看不見的 \\0）"
runp './dog_greet AAAAAAAAAAAAAAAA' 2.5
say "16 個 A：多出來的 \\0 已經跑出格子外"
runp 'for n in 8 15 16 24 32 40; do ./dog_greet $(printf "A%.0s" $(seq $n)) >/dev/null 2>&1; echo "$n 個 A → 結束碼 $?"; done' 3
say "139 = 128 + 11，11 號訊號就是 SIGSEGV（segfault）"
runp 'kill -l 11' 3

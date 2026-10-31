. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "防禦小勝：同一份程式、同一串輸入，換編譯方式"
runp 'P=AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD' 0.5
say "① 這台 Debian 的 gcc 預設：沒開 stack protector"
runp 'gcc -Q --help=common | grep -E "fstack-protector(-strong)? "' 3
runp 'gcc -o g_default dog_greet.c && ./g_default $P; echo "結束碼 $?"' 2.5
say "② 加 canary（金絲雀）：-fstack-protector-strong"
runp 'gcc -fstack-protector-strong -o g_canary dog_greet.c && ./g_canary $P; echo "結束碼 $?"' 3
say "③ -O2 -D_FORTIFY_SOURCE=2：編譯器知道 buf 只有 16"
runp 'gcc -O2 -D_FORTIFY_SOURCE=2 -o g_fortify dog_greet.c && ./g_fortify $P; echo "結束碼 $?"' 3
say "④ ASan：開發時用，直接告訴你哪一行、寫了幾格"
runp 'gcc -g -fsanitize=address -o g_asan dog_greet.c && ./g_asan $P 2>&1 | grep -E "ERROR|WRITE of size|#1 |overflows this"' 5
say "134 = 128 + 6（SIGABRT）：程式自己喊停，不是亂跳"

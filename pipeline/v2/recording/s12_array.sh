. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "陣列 = 一排連續的格子，用編號（從 0 開始）取用"
runp 'grep -v "^#" array.c' 2.5
runp 'gcc -o array array.c && ./array' 3.5
say "位址每次 +4：一格 int 佔 4 bytes，緊緊排在一起"
say "C 不會幫你檢查編號有沒有超出範圍——記住這句"

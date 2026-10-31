. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "作業預覽：自己寫 strlen——從頭往後走，遇到 \\0 就停"
runp 'sed -n "3,9p" my_strlen.c' 3
runp 'gcc -o my_strlen my_strlen.c && ./my_strlen' 3.5
say "跟標準函式庫結果一樣。這 5 行，就是 C 字串的全部祕密"

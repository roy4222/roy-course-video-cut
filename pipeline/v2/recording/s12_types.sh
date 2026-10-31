. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "型別 = 這格記憶體有多大、裡面的 0 和 1 要怎麼解讀"
runp 'cat types.c' 3
runp 'gcc -o types types.c && ./types' 4
say "char 'A' 其實就是數字 65；一個 byte 最大 255，再加 1 就繞回 0"

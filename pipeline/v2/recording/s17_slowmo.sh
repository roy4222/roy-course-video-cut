. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source slow.sh
say "慢放三次：strcpy 剛做完，偷看 buf 附近的記憶體"
say "第 1 次：8 個 A（0x41 就是 A）"
runp 'slow AAAAAAAA' 3
say "第 2 次：16 個 A，第三格的尾巴被 \\0 咬掉一格"
runp 'slow AAAAAAAAAAAAAAAA' 3.5
say "第 3 次：A×8 B×8 C×8 D×8，每 8 格換一個字母"
runp 'slow AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD' 4
say "第四格原本是返回位址 0x4011b1，現在是 DDDDDDDD"

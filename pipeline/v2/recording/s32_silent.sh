. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec32
say "現場寫一個小 bug：玩具 LiDAR 解析器，找最近的障礙物"
runp 'cat -n scan.c | sed -n "9,18p"' 4
say "第 15 行：i <= n。多跑了一格。你看出來了嗎？"
runp 'cat scan_ok.txt' 1.5
runp 'gcc -g -o scan scan.c && ./scan scan_ok.txt; echo "結束碼 $?"' 3
say "沒有崩潰，結束碼 0。可是資料裡最近是 95 公分，它說 0"
say "這就是最可怕的：沉默。現在加一個參數"
runp 'gcc -g -fsanitize=address -o scan_asan scan.c' 1.5
runp './scan_asan scan_ok.txt 2>&1 | grep -E "ERROR|READ|#0|located|allocated|#1 .*scan.c"' 5
say "heap-buffer-overflow、讀了 4 bytes、第 16 行；剛好超出 16 bytes 的區塊，在第 10 行 malloc 的"

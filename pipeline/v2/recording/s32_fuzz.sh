. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec32
say "修好 off-by-one 之後，v2 還藏一個洞。這次不用眼睛找，讓機器亂試"
runp 'cat -n scan2.c | sed -n "17,19p"' 3
runp 'sed -n "6,11p" fuzz_scan.py' 3
say "先拿沒有 ASan 的版本跑"
runp 'gcc -g -o scan2 scan2.c && python3 fuzz_scan.py ./scan2' 3.5
say "試到第 25 次才倒，而且遺言是 free(): invalid pointer——指向錯的地方"
say "換成 ASan 版本，同樣的亂試"
runp 'gcc -g -fsanitize=address -o scan2_asan scan2.c && python3 fuzz_scan.py ./scan2_asan' 3.5
say "第 2 次就抓到：stack-buffer-overflow，第 19 行，就是 hist[dist/100]"
runp 'cat crash.txt' 2
say "1093 公分：超過 9 公尺，格子只有 10 個。存下這個輸入，修完再跑一次"

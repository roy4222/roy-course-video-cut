. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/go2re/unitree_sdk2/thirdparty/lib/x86_64
say "快速秀：拿一個真實的 .so——Unitree SDK2 裡附的 DDS 函式庫（開源）"
runp 'ls -l libddsc.so; file -L libddsc.so | cut -c1-90' 3
say "先數數看：裡面有多少段可讀的文字？"
runp 'strings libddsc.so | wc -l' 2
say "找版本：編譯路徑會洩漏它是哪個專案、哪一版（使用者名稱已遮）"
runp 'strings libddsc.so | grep -m2 "cyclonedds-" | sed "s#/home/[^/]*/#/home/***/#"' 3.5
say "Cyclone DDS 0.10.2。知道版本，就能去查它有沒有已知漏洞"
say "再看它開了哪些保護：Project 1 的 Q3、Q7 就是在跟這些打交道"
runp "$SEC_LAB/sec22/.venv/bin/pwn checksec libddsc.so 2>&1 | sed -n \"2,6p\"" 4
say "Canary、NX、PIE 都有，RELRO 只開一半。作業裡的題目，是把這些一個個關掉再給你"

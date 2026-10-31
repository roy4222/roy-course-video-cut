. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
say "第三、四層：ASLR + PIE——每次執行，位址都換地方"
runp 'for i in 1 2 3; do ./v3_pie x | head -1; done' 3
say "沒有 PIE 的版本：程式本體永遠在同一個位址"
runp 'for i in 1 2 3; do ./v2_nx x | head -1; done' 3
say "關掉 ASLR（setarch -R）看看：每次都一樣"
runp 'for i in 1 2; do setarch -R ./v3_pie x | head -1; done' 3
say "隨機有多大？核心設定："
runp 'sudo cat /proc/sys/vm/mmap_rnd_bits' 2.5
say "28 bits ≈ 2 億 6 千萬種起點。實測 300 次："
runp 'python3 aslr_bits.py 300' 4
say "位址全變，但函式之間的距離不變 → 只要洩漏一個位址，全部都算得出來"

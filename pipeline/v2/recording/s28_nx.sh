. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
say "第二層：NX（不可執行）。資料區只能讀寫，不能當程式跑"
runp 'readelf -lW v1_canary | grep GNU_STACK; readelf -lW v2_nx | grep GNU_STACK' 3.5
say "RWE = 可讀、可寫、可執行；RW = 只能讀寫"
say "以前攻擊者把程式碼塞進堆疊再跳過去；NX 讓這招直接失效"
runp 'grep -o -m1 -w nx /proc/cpuinfo' 2.5
say "這需要 CPU 支援：每個記憶體分頁都有一個「不准執行」位元"

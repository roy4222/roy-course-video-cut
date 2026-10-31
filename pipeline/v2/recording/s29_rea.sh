. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
date +%s.%N > /tmp/s29_mark_0
say "換 REA 交叉驗證：在整個函式庫裡找 5f c3 這兩個 byte"
date +%s.%N > /tmp/s29_mark_a
runp 'rea search-bytes libddsc.so.0 5fc3 --limit 4 --format json | python3 hits.py' 0.1
date +%s.%N > /tmp/s29_mark_b
sleep 3
say "REA 的位址從 0x100000 起算：0x12e94b 就是剛才那塊"
say "它藏在 ddsi_tcp_select 的收尾：CycloneDDS 的 TCP 傳輸程式"
say "兩個工具，同一個答案：積木是真的，就在你的機器人函式庫裡"

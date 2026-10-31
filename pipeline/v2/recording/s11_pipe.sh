. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box; cd ~/fenris_ws/log
say "機器狗跑了一下午，log 有幾行？wc -l"
runp 'wc -l robot.log'
say "只看錯誤：grep 篩選"
runp 'grep ERROR robot.log | head -5' 2.5
say "| 管線：前一個指令的輸出，直接餵給下一個"
say "哪個節點最常出錯？抽欄位 → 排序 → 計數 → 再排序"
runp "grep ERROR robot.log | awk '{print \$3}' | sort | uniq -c | sort -nr" 3.5
say "> 存成檔案（覆蓋），>> 接在後面（追加）"
runp 'grep ERROR robot.log > errors.txt; wc -l errors.txt'
runp 'echo "--- 檢查完畢 $(date +%H:%M)" >> errors.txt; tail -2 errors.txt' 2.5
say "2>/dev/null：把錯誤訊息丟進黑洞"
runp 'cat no_such.log' 1.5
runp 'cat no_such.log 2>/dev/null; echo "（安靜了）"' 2
say "逆向預告：同一招拿去拆機器狗 SDK 的函式庫"
runp "strings $SEC_LAB/sdk/libddsc.so.0 | grep -i \"cyclone\" | sort -u | head -5" 3.5

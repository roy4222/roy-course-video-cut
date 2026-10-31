. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec33
say "同一個 LiDAR 解析器，用 Rust 寫，連 off-by-one 都照抄"
runp 'sed -n "11,14p" scan.rs' 3
runp 'rustc -g -o scan_rs scan.rs && ./scan_rs scan_ok.txt; echo "結束碼 $?"' 3.5
say "C 版沉默地答 0；Rust 版停下來，說出長度 4、索引 4、第 13 行"
say "修好的版本：不用索引，用 get，超出範圍就回傳 None"
runp 'sed -n "11,17p" scan_fixed.rs' 4
runp 'rustc -O -o scan_fixed scan_fixed.rs && ./scan_fixed scan_ok.txt && ./scan_fixed crash.txt; echo "結束碼 $?"' 3.5
say "SEC32 讓 C 倒下的那筆 1093，這裡變成一行說明，狗安全地停下"
say "但 Rust 有逃生門：unsafe。關掉檢查，會怎樣？"
runp 'sed -n "6,8p" scan_unsafe.rs' 3
runp 'rustc -O -o scan_unsafe scan_unsafe.rs && ./scan_unsafe; echo "結束碼 $?"' 3
say "這次是 Illegal instruction。unsafe 裡的錯，行為就不可預測了"
say "成本：編譯時間和檔案大小（同一台機器、同一個功能）"
runp 'time gcc -O2 -o scan_c scan.c' 2
runp 'time rustc -O -C strip=symbols -o scan_fixed scan_fixed.rs' 2
runp 'ls -l scan_c scan_fixed | awk "{print \$5, \$9}"' 3

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source $SEC_LAB/sec22/.venv/bin/activate; export PWNLIB_NOTERM=1
say "pwntools 也是放大鏡：checksec 看一個程式開了哪些保護"
runp 'pwn checksec ../../sec17/dog_greet 2>&1 | grep -E "Stack|NX|PIE|RELRO"' 3
say "SEC17 的玩具：No canary（我們故意關的）"
say "換一個真實的系統函式庫：上集的 Brotli 解碼器"
runp 'pwn checksec /usr/lib/x86_64-linux-gnu/libbrotlidec.so.1 2>&1 | grep -E "Stack|NX|PIE|RELRO"' 3
say "真貨：canary、NX、PIE 全開"
runp 'strings -n 8 /usr/lib/x86_64-linux-gnu/libbrotlidec.so.1 | grep -m5 BrotliDecoder' 3
say "strings 一秒看出它對外提供哪些函式"

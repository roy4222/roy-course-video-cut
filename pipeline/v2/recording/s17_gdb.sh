. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "用 gdb 問：buf 在哪？返回位址存在哪？"
runp "gdb -q -nx -batch -ex 'break 7' -ex 'run AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD' -ex 'print &buf' -ex 'info frame' ./dog_greet 2>/dev/null | grep -E 'buf|saved rip|rip at'" 4
say "算距離：返回位址的位置 − buf 的位置"
runp "gdb -q -nx -batch -ex 'break 7' -ex 'run x' -ex 'print (long)((char*)\$rbp + 8 - (char*)buf)' ./dog_greet 2>/dev/null | grep '^\\$'" 2.5
say "24：第 25 個字開始，就蓋到返回位址"
say "讓它跑到崩潰，看它死在哪一行指令"
runp "gdb -q -nx -batch -ex 'run AAAAAAAABBBBBBBBCCCCCCCCDDDDDDDD' -ex 'x/i \$rip' -ex 'x/gx \$rsp' ./dog_greet 2>/dev/null | grep -vE '^\$|Thread|libthread'" 5
say "死在 ret：它想跳去 0x4444444444444444，那裡什麼都沒有"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
say "NX 之後，攻擊者不寫新碼，改借現成的。真的函式庫裡有多少塊？"
runp 'ROPgadget --binary /bin/ls | tail -1' 2
runp 'ROPgadget --binary libddsc.so.0 | tail -1' 2.5
runp 'ROPgadget --binary ros_libs/librclcpp.so | tail -1' 3
say "每一塊都是「幾條指令 + ret」：做一點事，然後跳去下一塊"
runp 'ROPgadget --binary libddsc.so.0 | grep -E ": pop r(di|si) ; ret$"' 3
say "挑 0x2e94b 這塊：pop rdi ; ret。可是編譯器真的寫過這行嗎？"
runp 'objdump -d -M intel --start-address=0x2e946 --stop-address=0x2e94d libddsc.so.0 | tail -4' 3.5
say "編譯器寫的是 pop r15 ; ret，三個 byte：41 5f c3"
runp 'objdump -d -M intel --start-address=0x2e94b --stop-address=0x2e94d libddsc.so.0 | tail -2' 3.5
say "從中間一個 byte 開始讀：5f c3 = pop rdi ; ret"
say "x86 指令長短不一，同一串 byte 換個起點就是另一段程式"

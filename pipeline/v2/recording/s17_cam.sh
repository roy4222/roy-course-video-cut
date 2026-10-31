. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "機器人版本：一個假的相機封包解析器（玩具，不是真驅動）"
runp "sed -n '7,19p' cam_packet.c" 4
runp 'gcc -O0 -fno-stack-protector -U_FORTIFY_SOURCE -o cam_packet cam_packet.c' 1
say "封包前 2 bytes 是長度。正常包：48 bytes"
runp 'xxd good.pkt | head -2' 2.5
runp './cam_packet good.pkt' 2
say "壞包：c8 00 = 200，可是 frame 只有 64 格"
runp 'xxd evil.pkt | head -2' 2.5
runp './cam_packet evil.pkt; echo "結束碼 $?"' 3
say "修正版：先檢查長度，再複製"
runp 'gcc -DFIXED -o cam_packet_fixed cam_packet.c && ./cam_packet_fixed evil.pkt; echo "結束碼 $?"' 3.5

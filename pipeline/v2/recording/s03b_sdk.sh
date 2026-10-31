. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "交叉驗證：官方 unitree_sdk2（BSD-3）怎麼命名主題？"
run 'grep -n "rt/api/\|/request" unitree_sdk2/include/unitree/robot/channel/channel_namer.hpp; grep -n "SERVICE_NAME" unitree_sdk2/include/unitree/robot/go2/sport/sport_api.hpp' 4
say "rt/api/ + sport + /request = 跟社群表一字不差"
say "比對兩張 api_id 表：官方標頭檔 vs 社群逆出來的"
run '.venv/bin/python compare_ids.py' 6
say "不同的那幾個：官方用 1.1.7 起的 MCF 編號，社群表是舊模式（legion1581 有註解）"
run 'grep -n "MCF (Multi-Control" -A2 unitree_webrtc_connect/unitree_webrtc_connect/constants.py' 4
say "最後直接看機器碼：Hello() 到底送幾號？"
run 'objdump -dr -C --no-show-raw-insn sdkobj/sport_client_go2.o | awk "/<unitree::robot::go2::SportClient::Hello\\(\\)>:/,/^\$/" | grep -E "0x3f8|Client::Call" | cut -c1-100; python3 -c "print(0x3f8)"' 5

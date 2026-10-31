. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd go2_ros2_sdk/go2_robot_sdk/go2_robot_sdk
say "動作編號表：api_id。這張表就是逆向的成果"
run 'sed -n "10,30p" domain/constants/robot_commands.py' 4
say "主題（topic）表：rt/ 開頭，跟官方 DDS 名字一樣"
run 'grep -n "rt/" domain/constants/webrtc_topics.py | head -16' 4
say "訊息種類：validation、subscribe、msg、vid…"
run 'grep -n "\"VALIDATION\"\|\"SUBSCRIBE\"\|\"MSG\"\|\"VID\"\|\"HEARTBEAT\"" domain/constants/webrtc_topics.py' 3
cd $SEC_LAB/go2re
say "離線產生一則 Hello 指令（只印出，不連線、不送出）"
run '.venv/bin/python gen_cmd_demo.py' 5

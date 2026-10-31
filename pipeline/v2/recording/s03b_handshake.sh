. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd go2_ros2_sdk/go2_robot_sdk/go2_robot_sdk/infrastructure/webrtc
say "握手第 1 步：向狗的 9991 埠要公鑰（con_notify）"
run 'grep -n "9991" http_client.py' 2.5
say "第 2 步：依韌體版本 data2=2 / data2=3 決定怎麼解開公鑰"
run 'grep -n "data2 ==\|def decrypt_con_notify" go2_connection.py' 3
run 'grep -n "key = bytes" go2_connection.py | sed -E "s/\[[0-9, ]+\]/[▒▒ 16 bytes 已遮蔽 ▒▒]/"' 3
say "第 3 步：自己產生 AES 鑰匙加密 SDP，再用狗的 RSA 公鑰包住鑰匙"
run 'grep -n "aes_encrypt(new_sdp\|rsa_encrypt(aes_key\|con_ing_" go2_connection.py http_client.py' 3.5
say "第 4 步：資料通道打開後，狗出一道題，答案 = MD5(\"UnitreeGo2_\" + 題目)"
run 'grep -n "UnitreeGo2_\|Validation Ok" crypto/encryption.py go2_connection.py' 3.5
cd $SEC_LAB/go2re
say "用假題目跑一次算法（純離線）"
run '.venv/bin/python -c "import hashlib,base64;q=\"demo-challenge\";print(base64.b64encode(hashlib.md5((\"UnitreeGo2_\"+q).encode()).digest()).decode())"' 3

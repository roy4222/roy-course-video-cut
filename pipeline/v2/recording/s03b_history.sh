. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "時間線 1：tfoldi 第一次打通 WebRTC（2024-02-13）"
run 'git -C go2-webrtc log --reverse --format="%ad  %s" --date=short | head -4' 3
say "當年連線埠是 8081，token 靠側錄 App 流量取得（他的 README 寫的）"
run 'grep -n "8081\|sniff\|ngrep" go2-webrtc/README.md | cut -c1-105' 4
say "時間線 2：一週後，ROS 2 SDK 誕生；之後每次韌體更新都要追"
run 'git -C go2_ros2_sdk log --reverse --format="%ad  %s" --date=short | grep -i -E "first commit|lidar support|new method for webrtc|RSA key format|AES-128" ' 5
say "證據：legion1581 的程式註解直接寫『對應 Unitree apk 裡的 …』"
run 'grep -n -i "apk" unitree_webrtc_connect/unitree_webrtc_connect/unitree_auth.py unitree_webrtc_connect/unitree_webrtc_connect/unitree_cloud.py | cut -c1-118 | head -6' 5

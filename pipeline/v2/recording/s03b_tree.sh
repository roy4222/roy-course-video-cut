. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "主角：abizovnuralem/go2_ros2_sdk（BSD-2），已 clone 到 box"
run 'cd go2_ros2_sdk && git log --oneline | wc -l && git log --reverse --format="%ad %an  %s" --date=short | head -1' 2.5
run 'tree -d -L 3 go2_robot_sdk/go2_robot_sdk | head -24' 4
say "四層：domain 放常數、infrastructure 放 WebRTC 與解碼、presentation 是 ROS 2 節點"
run 'ls go2_robot_sdk/go2_robot_sdk/domain/constants go2_robot_sdk/go2_robot_sdk/infrastructure/webrtc' 3
say "README 自己寫明：WebRTC 這條路是誰先打通的"
run 'grep -n -i "tfoldi\|legion1581" README.md | cut -c1-110' 4
cd ..

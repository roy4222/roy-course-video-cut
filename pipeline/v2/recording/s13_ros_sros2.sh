. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export PSUSER=box HOME=$FENRIS_HOME; cd ~
E="-e ROS_DOMAIN_ID=42 -e FASTDDS_BUILTIN_TRANSPORTS=UDPv4"
S="-e ROS_SECURITY_KEYSTORE=/keys/ks -e ROS_SECURITY_ENABLE=true -e ROS_SECURITY_STRATEGY=Enforce -e ROS_SECURITY_ENCLAVE_OVERRIDE=/fenris/dog -v $FENRIS_ROOT/keys:/keys:ro"
sudo docker rm -f fenris_dog >/dev/null 2>&1; sudo rm -rf "$FENRIS_ROOT/keys/ks"
say "修法：SROS2（ROS 2 內建的 DDS-Security）。先做鑰匙圈，再發給狗一個身分"
runp 'sudo docker run --rm $E -v $FENRIS_ROOT/keys:/keys ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; ros2 security create_keystore /keys/ks >/dev/null; ros2 security create_enclave /keys/ks /fenris/dog >/dev/null; ls /keys/ks/enclaves/fenris/dog"' 3
say "狗重新開機，打開三個開關：ENABLE=true、STRATEGY=Enforce、指定身分"
runp 'sudo docker run -d --name fenris_dog --network host $E $S ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; ros2 topic pub -r 1 /fenris/status std_msgs/msg/String \"{data: battery=87%_mode=guide_owner=roy}\" >/dev/null & ros2 topic echo /cmd_vel geometry_msgs/msg/Twist" | cut -c1-12' 5
stranger(){ printf "\033[1;31mstranger@cafe-laptop\033[0m:\033[1;34m~\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; sudo docker run --rm --network host $E ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; $1" 2>/dev/null; sleep ${2:-2}; }
owner(){ printf "\033[1;32mroy@owner-laptop\033[0m:\033[1;34m~\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; sudo docker run --rm --network host $E $S ros:jazzy-ros-core bash -c "source /opt/ros/jazzy/setup.bash; $1" 2>/dev/null; sleep ${2:-2}; }
say "陌生筆電再試一次："
stranger 'ros2 topic list --no-daemon --spin-time 3' 2
stranger 'timeout 8 ros2 topic echo /fenris/status --once || echo "（8 秒，什麼都沒收到）"' 2.5
say "有鑰匙的主人筆電："
owner 'ros2 topic list --no-daemon --spin-time 3' 2
owner 'ros2 topic echo /fenris/status --once' 3
say "同一個網路，沒有身分的人連 topic 名字都看不到"
sudo docker rm -f fenris_dog >/dev/null 2>&1

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
say "checksec：一秒看出一個程式穿了幾層防彈衣"
runp 'checksec /bin/ls' 3
say "同一份 guard.c，我用四種編譯選項各編一次"
runp 'for v in v0_none v1_canary v2_nx v3_pie; do echo "== $v"; checksec $v 2>&1 | grep -E "Stack|NX|PIE"; done' 5
say "真實機器人函式庫呢？Go2 SDK 附的 CycloneDDS、ROS 2 的 rcl"
runp 'checksec libddsc.so.0 ros_libs/librcl.so 2>&1 | grep -E "\]|RELRO|Stack|NX"' 4.5
say "都有 Canary、NX；RELRO 只有 Partial——之後會用到這個差別"

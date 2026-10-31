. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/mit
say "Go2 SDK 也附了 ARM（aarch64）版，給機器人上的板子用"
runp 'file libddsc_arm64.so.0 | cut -c1-72' 2
say "ARM 每條指令固定 4 bytes，不能從中間讀。數數 ret 和 PAC："
runp 'python3 arm_ret.py libddsc_arm64.so.0' 3.5
say "ret 少很多（沒有「藏在中間」的積木），但 PAC 一個都沒開"
runp 'checksec libddsc_arm64.so.0 2>&1 | grep -E "Arch|RELRO|Stack|NX"' 3

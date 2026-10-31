. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source $SEC_LAB/sec22/.venv/bin/activate; export PWNLIB_NOTERM=1
say "機器狗版：用 pwntools 寫 15 行迷你 fuzzer"
say "對象：SEC17 我們自己寫的相機封包解析器"
runp 'cat fuzz_cam.py' 4
runp 'python fuzz_cam.py ./cam_packet' 4
say "65～80 已經寫出界，卻「看起來正常」"
say "換上 ASan 版本再跑一次"
runp 'python fuzz_cam.py ./cam_packet_asan' 4
say "65 就抓到：fuzzer + ASan，是找 bug 的黃金組合"

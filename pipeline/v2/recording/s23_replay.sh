. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source $SEC_LAB/sec22/.venv/bin/activate; export PWNLIB_NOTERM=1
say "通關回放 1／3：pwntools 打開程式、送出答案"
runp 'python solve0.py 2>/dev/null | tail -1' 2.5
say "通關回放 2／3：換成網路連線，同一招"
runp '(python serve.py &); sleep 1; python remote0.py 2>/dev/null | tail -1; pkill -f "python serve.py"' 3
say "通關回放 3／3：fuzzer + ASan，65 bytes 就抓到越界"
runp 'python fuzz_cam.py ./cam_packet_asan | sed -n "3,5p"' 3
say "三面旗，全部在自己的電腦上拿到"

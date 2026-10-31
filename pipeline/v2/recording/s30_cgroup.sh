. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/iso
say "cgroups：限制資源。給「AI 模型容器」64 MB 上限，讓它硬要 200 MB"
runp "sudo docker run --rm -m 64m --memory-swap 64m ros:jazzy-ros-core python3 -c 'b=bytearray(200<<20)'; echo exit=\$?" 3.5
say "137 = 128 + 9：被核心用 SIGKILL 砍掉。主機上的其他程式毫髮無傷"

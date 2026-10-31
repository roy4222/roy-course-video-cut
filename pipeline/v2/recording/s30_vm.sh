. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd "$FENRIS_ROOT/vm"
xt(){ sleep $2; W=$(xdotool search --class xterm|head -1); xdotool windowfocus --sync $W; xdotool type --delay 55 "$1"; xdotool key Return; }
say "三層對照：主機、容器、虛擬機，各自跑的是哪顆核心？"
runp 'uname -r' 1.8
runp 'sudo docker run --rm alpine:3.22 uname -r' 3
say "容器 = 同一顆核心。現在開一台真的虛擬機（QEMU，256 MB，Alpine 核心）"
runp 'tail -3 vm.sh' 2.5
( xt "/bin/busybox uname -r" 40; xt "/bin/busybox mount -t proc p /proc; /bin/busybox head -1 /proc/meminfo" 3; sleep 4; W=$(xdotool search --class xterm|head -1); xdotool windowfocus --sync $W; xdotool key ctrl+a; xdotool type x ) &
runp './vm.sh' 0.3
wait
clear
say "整理一下三層各自的核心："
runp 'uname -r' 1.5
runp 'sudo docker run --rm alpine:3.22 uname -r' 3
say "虛擬機裡：6.12.114-0-virt——它有自己的核心、自己的 256 MB 記憶體"
say "容器逃逸只要打穿共用的核心；虛擬機逃逸得先打穿 hypervisor"

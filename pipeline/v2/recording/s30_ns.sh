. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/iso
say "主機上：數一數行程，看核心版本"
runp 'ps -e --no-headers | wc -l; uname -r' 2.5
say "開一個容器，在裡面做一樣的事（這台的 docker 要 sudo，等等會說為什麼）"
runp "sudo docker run --rm alpine:3.22 sh -c 'ps; uname -r; id -u'" 3.5
say "只看得到自己的行程（PID namespace）——但核心版本一模一樣"
say "裡面是 root（uid 0），可是權限被削過。看能力位元："
runp "sudo docker run --rm alpine:3.22 grep CapEff /proc/self/status | python3 capdecode.py" 3.5
runp "sudo docker run --rm --privileged alpine:3.22 grep CapEff /proc/self/status | python3 capdecode.py | head -1" 3
say "預設 14 種，--privileged 一次給滿 41 種。少了 net_admin 會怎樣？"
runp "sudo docker run --rm alpine:3.22 ip link add d0 type dummy" 2.5
say "再收緊：一種能力都不給，檔案系統唯讀"
runp "sudo docker run --rm --cap-drop ALL --read-only alpine:3.22 touch /x" 3

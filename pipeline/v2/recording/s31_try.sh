. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec31
say "try-this：一個行程到底握有多少權限？先看我自己的 shell"
runp './privs.sh' 3
say "Uid 1000、CapEff 全 0：普通人，沒有特殊能力"
say "再看這台機器上的 sshd 監聽行程"
runp './privs.sh $(pgrep -f "sshd -p 2222" | head -1)' 3.5
say "Uid 0、CapEff 一長串 f：root，什麼都能做——所以它把工作拆出去"
runp 'ssh -V; ls /usr/lib/openssh/ | grep sshd' 3.5
say "sshd-auth 管登入前、sshd-session 管連線：OpenSSH 10.0 的拆法"
say "CTF 小關，60 秒：這個沙箱本來只該給相機照片。找出它多開的那扇窗"
runp './ctf_box.sh "ls /"' 3
say "（暫停影片，自己想一下……）"
sleep 3
runp './ctf_box.sh "ls -R /data"' 3
runp './ctf_box.sh "cat /data/config/flag.txt"' 3
say "/data 把整個資料夾都掛進來了，設定檔也跟著進去。窗開太大，沙箱就白做"

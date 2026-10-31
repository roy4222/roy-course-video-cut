cd $SEC_LAB/sec36/repo
say "MIT 6.566 Lab 1 的公開 repo：分支 lab1"
runp 'git log --oneline | head -3; ls' 3.5
say "clean-env.sh：為什麼每次都要用它啟動伺服器？"
runp 'grep -nE "ulimit|exec env|setarch" clean-env.sh' 3.5
say "第一招：env - 把環境變數清空。環境變數放在堆疊頂端，多一個字，位址就會移"
runp 'env | wc -l; env - env | wc -l' 2.5
say "第二招：setarch -R 關掉位址隨機化（ASLR）。先看平常：堆疊位置每次都變"
runp 'grep stack /proc/self/maps; grep stack /proc/self/maps' 3
runp 'setarch $(uname -m) -R grep stack /proc/self/maps; setarch $(uname -m) -R grep stack /proc/self/maps' 3
say "關掉之後，兩次一模一樣。實驗才會「可重現」——評分也用同一套"
say "把 web 伺服器 zookd 編起來，在實驗機 18080 埠跑幾秒，示範完就關"
runp 'gcc -std=c99 -D_GNU_SOURCE -fno-stack-protector -g -c zookd.c http.c 2>/dev/null; gcc zookd.o http.o -o zookd && ls -l zookd' 2.5
PATH=$SEC_LAB/sec36/.venv/bin:$PATH setarch $(uname -m) -R ./zookd 18080 >/tmp/w36_zookd.log 2>&1 &
sleep 1
runp 'curl -s -i http://127.0.0.1:18080/index.html | head -4' 3
runp 'curl -sL http://127.0.0.1:18080/zoobar/index.cgi/ | grep -A1 "<title>" | tail -1' 3
say "對伺服器來說，一個 HTTP 請求就是一次遠端 API 呼叫。Lab 1 的戰場，就在 http.c 怎麼讀這個請求"
pkill -f "zookd 18080"
runp "pgrep -c zookd || echo 已關閉"

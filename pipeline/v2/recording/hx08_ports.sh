. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "實驗：在自己電腦開兩個玩具服務，看看誰把門開到外面"
runp 'python3 toy_service.py 127.0.0.1 8871 2>/dev/null & python3 toy_service.py 0.0.0.0 8872 2>/dev/null & sleep 1' 0.5
say "誰在聽？ss = 列出正在等連線的程式"
runp 'ss -ltn | grep -E "State|887"' 2.5
say "127.0.0.1 = 只有自己能連；0.0.0.0 = 同網段的人都能連"
say "用 nmap 只掃自己（127.0.0.1），不掃別人"
runp 'nmap -Pn -p 8860-8880 127.0.0.1 | grep -E "PORT|open"' 2.5
say "沒有密碼的管理頁，連上去長這樣："
runp 'curl -s http://127.0.0.1:8872/' 2
say "收工：把玩具服務關掉"
runp 'kill %1 %2; sleep 0.5; ss -ltn | grep -c 887' 2

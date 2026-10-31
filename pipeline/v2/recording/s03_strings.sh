. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "關卡1：一個只有執行檔、沒有原始碼的機器狗解鎖程式"
run 'ls -l dog_unlock_v1'
run 'file dog_unlock_v1' 2.5
say "先亂猜一次密碼"
run 'echo 1234 | ./dog_unlock_v1'
say "逆向第一招：strings —— 把檔案裡看得懂的文字全挖出來"
run 'strings -n 8 dog_unlock_v1 | head -16 | grep --color=always -E "woof.*|$"' 5
say "看到可疑的東西了？試試看"
run 'echo woof-2026-guide | ./dog_unlock_v1' 3
say "破解完成：10 秒，一個指令"

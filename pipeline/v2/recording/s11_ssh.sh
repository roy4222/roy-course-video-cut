. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box; cd ~; rm -rf ~/.ssh
alias ssh='ssh -o UserKnownHostsFile=$FENRIS_HOME/.ssh/known_hosts -o BatchMode=yes -o IdentitiesOnly=yes'
shopt -s expand_aliases
say "SSH 金鑰 = 不用打密碼就能登入機器狗的鑰匙"
say "這台 lab 開了一隻『模擬機器狗』帳號 unitree（port 2222）"
runp 'mkdir ~/.ssh && ssh-keygen -t ed25519 -N "" -q -f ~/.ssh/go2_key && ls -l ~/.ssh' 2.5
ssh-keyscan -p 2222 127.0.0.1 > ~/.ssh/known_hosts 2>/dev/null
say "go2_key = 私鑰（絕不外流），.pub = 公鑰（放到機器上）"
say "把公鑰放進機器狗的 authorized_keys（平常用 ssh-copy-id）"
runp 'sudo cp ~/.ssh/go2_key.pub /home/unitree/.ssh/authorized_keys'
say "如果私鑰權限太鬆，例如 644，會怎樣？"
runp 'chmod 644 ~/.ssh/go2_key'
runp 'ssh -p 2222 -i ~/.ssh/go2_key unitree@127.0.0.1 "echo 已登入: \$(whoami)"' 4.5
say "ssh 拒用：別人讀得到的私鑰，已經不算祕密"
runp 'chmod 600 ~/.ssh/go2_key && chmod 700 ~/.ssh'
runp 'ls -ld ~/.ssh; ls -l ~/.ssh' 2.5
runp 'ssh -p 2222 -i ~/.ssh/go2_key unitree@127.0.0.1 "echo 已登入: \$(whoami)"' 3
say "口訣：.ssh 資料夾 700，私鑰 600，公鑰 644"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box PATH=/usr/local/bin:/usr/bin:/bin; cd ~
say "打 ls 時，系統怎麼知道 ls 在哪？答案在 \$PATH"
runp 'echo $PATH | tr ":" "\n"' 2.5
runp 'which ls python3' 2
say "PATH 由左往右找，先找到的先執行"
say "如果有人在最前面塞一個假的 ls……"
runp 'mkdir -p /tmp/evil && printf "#!/bin/sh\necho \"[假 ls] 我先被找到了，身分: \$(id -un)\"\n" > /tmp/evil/ls && chmod +x /tmp/evil/ls'
runp 'PATH=/tmp/evil:$PATH ls' 2.5
say "/tmp 是誰都能寫的資料夾（看那個 w 和 t）"
runp 'ls -ld /tmp' 2.5
say "所以：PATH 裡不能有別人能寫的資料夾，尤其 root"
runp 'rm -rf /tmp/evil' 1

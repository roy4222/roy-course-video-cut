. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box; cd ~/fenris_ws/scripts
say "startup.sh 開機時由 root 執行（模擬 systemd 服務）"
runp 'cat startup.sh'
runp 'sudo bash startup.sh' 2
say "有人嫌權限麻煩，下了一個很常見的指令……"
runp 'chmod 777 startup.sh'
runp 'ls -l startup.sh' 2.2
say "777 = 任何帳號都能改它。intruder 偷加一行："
runp "echo 'echo \"[!] intruder 的程式碼，現在身分: \$(id -un)\"' | sudo -u intruder tee -a startup.sh" 2
say "下次開機，root 照常執行它……"
runp 'sudo bash startup.sh' 3
say "intruder 的程式以 root 身分跑了 = 整台機器被拿走"
say "修好：擁有者改 root、權限 755、刪掉那行"
runp 'sudo sed -i "/intruder/d" startup.sh && sudo chown root:root startup.sh && sudo chmod 755 startup.sh'
runp 'ls -l startup.sh'
runp "echo 'echo hi' | sudo -u intruder tee -a startup.sh" 2.5
say "健檢：找出誰都能寫的檔案（-perm -0002）"
runp 'chmod 666 ~/fenris_ws/log/robot.log; find ~ -perm -0002 -type f' 3
runp 'chmod 644 ~/fenris_ws/log/robot.log'

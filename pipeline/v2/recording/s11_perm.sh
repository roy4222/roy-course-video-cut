. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
export HOME=$FENRIS_HOME PSUSER=box; cd ~/fenris_ws/src/guide_dog/config
say "ls -l 最左邊那串就是權限"
runp 'ls -l' 2.5
say "-rw-r--r--：擁有者可讀寫，同群組、其他人都可讀"
say "所以另一個帳號 intruder 也讀得到我的金鑰？"
runp 'sudo -u intruder cat cloud_secret.yaml' 2.5
say "讀到了。改成 600：只有我能讀寫"
runp 'chmod 600 cloud_secret.yaml'
runp 'ls -l cloud_secret.yaml'
runp 'sudo -u intruder cat cloud_secret.yaml' 2.5
say "數字怎麼來？r=4 w=2 x=1，三位數 = 我/群組/其他人"
runp 'stat -c "%A  %a  %n" cloud_secret.yaml params.yaml' 3

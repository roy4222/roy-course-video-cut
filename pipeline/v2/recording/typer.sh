. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
# source me. usage: say "註解"; run 'command'
PS_COLOR='\033[1;32m'; RST='\033[0m'
type_out(){ local s="$1"; for ((i=0;i<${#s};i++)); do printf '%s' "${s:$i:1}"; sleep 0.035; done; }
say(){ printf '\033[1;33m# '; type_out "$1"; printf "${RST}\n"; sleep 0.8; }
run(){ printf "${PS_COLOR}roy@lab${RST}:\033[1;34m~/re\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; eval "$1"; sleep ${2:-1.8}; }
# dynamic prompt version: shows label user and real cwd (~ = $HOME)
runp(){ local d=$(pwd); d=${d/#$HOME/\~}; printf "${PS_COLOR}${PSUSER:-roy}@lab${RST}:\033[1;34m${d}\033[0m\$ "; type_out "$1"; sleep 0.4; printf '\n'; eval "$1"; sleep ${2:-1.8}; }

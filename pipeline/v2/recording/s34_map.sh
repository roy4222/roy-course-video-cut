. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec34
say "技能點表：Project 1 七題的題型，在真實世界被利用過幾次？"
runp 'python3 skill_table.py' 6
say "資料是 CISA KEV：確定在野外被利用過的漏洞清單"
say "每一題都不是玩具：同一類的洞，真的上過新聞"

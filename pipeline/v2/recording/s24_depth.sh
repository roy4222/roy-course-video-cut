. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "縱深防禦：同一個 bug，再加一層——從原始碼修"
runp 'diff dog_photo_service.py dog_photo_service_fixed.py' 3.5
runp 'python3 dog_photo_service_fixed.py ../house/owner_notes.txt; echo "結束碼 $?"' 2.5
say "第 1 層擋輸入、第 2 層關沙盒：任一層失手，另一層還在"
say "攻擊者也是一層一層破：看本週 KEV 的一串連鎖"
runp "jq -r '.vulnerabilities[]|select(.cveID==\"CVE-2026-46300\")|.shortDescription' ../sec18/kev.json | fold -s -w 110" 4
say "PHP 的洞進門，核心的洞升到 root：每一層都破，才走得到底"
say "服務帳號：這台機器上，各身分各跑了多少行程？"
runp "ps -eo user= | sort | uniq -c | sort -rn | head -5" 3

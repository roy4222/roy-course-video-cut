. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec18
say "CS155 Part 1：五個 setuid root 程式。真實世界的同款：sudo"
runp 'jq ".vulnerabilities[] | select(.cveID==\"CVE-2021-3156\") | {cveID, dateAdded, shortDescription, cwes}" kev.json' 5
say "off-by-one 導致 heap 溢位，可以提權——CWE-193 就是 SEC32 的差一錯誤"
say "讀 advisory 第一步：我受影響嗎？受影響範圍 1.9.0 到 1.9.5p1，修在 1.9.5p2"
runp 'sudo -V | head -1' 2
runp 'dpkg --compare-versions 1.9.16p2 ge 1.9.5p2 && echo "1.9.16p2 >= 1.9.5p2：已在修補版本之後"' 3
say "第二步：攻擊面有多大？列出這台機器上所有 setuid 程式"
runp 'find /usr -perm -4000 -type f 2>/dev/null' 4
runp 'ls -l /usr/bin/sudo' 2.5
say "權限欄的 s：誰執行它，它都用擁有者 root 的身分跑。每一個都是一扇 root 的門"

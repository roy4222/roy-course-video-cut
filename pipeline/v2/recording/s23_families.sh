. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "漏洞家族速覽：拿今年 KEV 的 282 筆來分家"
runp "jq '[.vulnerabilities[]|select(.dateAdded>=\"2026-01-01\")]|length' kev.json" 2
say "對照表是我們自己訂的教學分類，不是官方分類"
runp 'sed -n "3,9p" families.jq | cut -c1-110' 4
runp "jq -r 'include \"families\"; [.vulnerabilities[]|select(.dateAdded>=\"2026-01-01\")|. as \$v|((\$v.cwes[0]//\"無\")|fam(\$v.notes))]|group_by(.)|map([length,.[0]])|sort|reverse[]|@tsv' -L . kev.json" 4
say "本週新增的 10 筆，各屬哪一家？"
runp "jq -r 'include \"families\"; .vulnerabilities[]|select(.dateAdded>=\"2026-10-24\")|. as \$v|\"\(((\$v.cwes[0]//\"無\")|fam(\$v.notes)))\t\(.cveID)  \((.vendorProject+\" \"+.product)[0:42])\"' -L . kev.json | sort" 5
say "供應鏈 = KEV 註明「影響開源元件／第三方函式庫」"

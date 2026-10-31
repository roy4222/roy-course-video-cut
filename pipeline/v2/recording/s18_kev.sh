. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
source kev.sh
say "CISA KEV：已確認「有人正在拿來攻擊」的漏洞清單，公開下載"
runp 'curl -s $KEV -o kev.json && jq "{catalogVersion, count}" kev.json' 3
say "這週（10/24 之後）新加了哪些？"
runp "jq -r '.vulnerabilities[]|select(.dateAdded>=\"2026-10-24\")|\"\(.dateAdded)  \(.cveID)  \(.vendorProject) \(.product)\"' kev.json | sort" 5
say "挑一個跟「記憶體」有關的：Google Brotli"
runp "jq '.vulnerabilities[]|select(.cveID==\"CVE-2026-111497\")|{cveID,vulnerabilityName,dateAdded,dueDate,knownRansomwareCampaignUse,cwes}' kev.json" 5
say "CWE-787 = 越界寫入。整份清單裡它排第幾？"
runp "jq -r '[.vulnerabilities[].cwes[]]|group_by(.)|map([length,.[0]])|sort|reverse|.[:5][]|@tsv' kev.json" 4

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "Passkey 為什麼不怕釣魚？同一把鑰匙，真網站 vs 假網站"
run 'node ../phish_test.mjs' 4
say "瀏覽器把網域綁進簽章：假網站連開口要的資格都沒有"
run "python3 -c \"import json;c=json.load(open('/tmp/pkvid/credentials.json'))['credentials'][0];print('rpId（綁定網域）:',c['rpId']);print('privateKey（只在你的裝置）:',c['privateKey'][:24]+'…');print('signCount:',c['signCount'])\"" 4
say "伺服器只拿到公鑰。資料庫被偷，也沒有密碼可以破"

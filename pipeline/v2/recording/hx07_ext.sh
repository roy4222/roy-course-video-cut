. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "實驗：自己做的玩具擴充功能（只在本機，不上架）"
runp 'ls ext_v1 ext_v2' 1.2
say "v1：一個記事小工具，只要求 storage"
runp 'python3 audit.py ext_v1/manifest.json' 2
say "模擬：開發者帳號被釣魚，攻擊者推出 v1.0.1"
runp 'diff <(python3 -m json.tool ext_v1/manifest.json) <(python3 -m json.tool ext_v2/manifest.json) | head -14' 2.5
say "同一個名字，權限多了什麼？"
runp 'python3 audit.py ext_v1/manifest.json ext_v2/manifest.json' 3
say "你的電腦：chrome://extensions → 詳細資料 → 網站存取權"
say "用不到的就移除；要用的改成「點擊時」"
sleep 1.5

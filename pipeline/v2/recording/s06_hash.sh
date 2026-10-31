. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "雜湊（hash）：把任何文字壓成固定長度的指紋，而且算不回去"
run 'echo -n dragon | sha256sum'
run 'echo -n dragon | sha256sum' 1.5
say "同樣輸入，永遠同樣輸出。改一個字母呢？"
run 'echo -n Dragon | sha256sum' 3
say "整串全變。網站應該只存這個指紋，不存密碼本身"
say "但如果網站只用 SHA-256、沒加鹽，資料庫被偷會怎樣？"
run 'python3 leak_demo.py' 6

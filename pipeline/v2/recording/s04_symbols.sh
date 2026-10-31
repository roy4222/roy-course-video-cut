. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "第一題：有符號的 dog_unlock_v2。叫 REA 用 Ghidra 做概覽"
run 'time rea analyze dog_unlock_v2 --provider ghidra --format json | nr | head -12' 3
say "請它反編譯 check_code"
run 'rea decompile dog_unlock_v2 --procedure check_code --provider ghidra --format json | nr' 5
say "每個結果都附 SHA-256 與『限制』說明"
run 'rea decompile dog_unlock_v2 --procedure check_code --provider ghidra --format json | nr limits 4' 5

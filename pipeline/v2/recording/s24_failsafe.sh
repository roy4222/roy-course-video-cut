. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "失敗安全 demo：導盲犬的障礙物感測，第 3 秒當掉（玩具模擬）"
runp "sed -n '9,13p' guide_dog_failsafe.py" 3
say "版本 A：沒有消息，就當作沒有障礙（fail-open）"
runp 'python3 guide_dog_failsafe.py open' 3.5
say "版本 B：沒有消息，就當作最壞情況（fail-safe）"
runp 'python3 guide_dog_failsafe.py safe' 3.5
say "壞掉時，預設要倒向「安全」那一邊"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "實驗：自己做一張「退款」QR Code（網址是假的 .example）"
runp 'python3 qr.py "https://www.165.gov.tw.check-refund.example/pay"' 2.5
say "掃之前先問：它到底要帶我去哪？"
runp 'python3 whereto.py "https://www.165.gov.tw.check-refund.example/pay"' 3
say "看起來像 165，真正的老闆是最右邊那段"
say "再來一個：西里爾字母 а 偽裝成英文 a"
runp 'python3 whereto.py "https://www.аpple.com/login"' 3
say "電腦眼中它叫 xn--pple-43d.com，不是 apple.com"
sleep 1.5

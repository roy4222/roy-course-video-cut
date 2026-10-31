. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "Authenticator App 的 6 位數，是怎麼算出來的？"
run 'python3 totp_demo.py qr' 4
say "QR 碼裡只有一串『種子』。之後完全不用網路，用時間算"
run 'python3 totp_demo.py 33' 2
say "手機和伺服器各算各的，因為種子和時間一樣，答案就一樣"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "正確做法：bcrypt —— 加鹽，而且故意算很慢"
run 'python3 bcrypt_demo.py' 6

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "我的密碼外洩過嗎？Have I Been Pwned 的密碼 API"
say "它用 k-匿名：只送出雜湊的前 5 碼"
run 'echo -n password123 | sha1sum'
run 'curl -s https://api.pwnedpasswords.com/range/CBFDA | head -5' 2.5
run 'python3 hibp_check.py password123' 3
run "python3 hibp_check.py 'Tr0ub4dor&3-fenris-2026'" 3

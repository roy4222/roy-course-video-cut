. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "關卡3：動態分析 —— 讓程式跑起來，在它比對密碼的瞬間按暫停"
run 'cat > /tmp/g.cmd <<X
break check_code
run < <(echo AAAAAAAAAAAAA)
x/13xb &secret
info registers rdi
continue
X'  0.5
run 'gdb -q -batch -x /tmp/g.cmd ./dog_unlock_v2 2>&1 | grep -v "^\[" ' 5
say "拿到 13 個位元組 + XOR 0x4a，用 Python 還原"
run 'python3 -c "print(bytes(b ^ 0x4a for b in bytes.fromhex(\"39233e67393e2b3367222f2f26\")).decode())"' 3
run 'echo sit-stay-heel | ./dog_unlock_v2' 3
say "三招：strings 看文字、objdump 看指令、gdb 看執行當下"

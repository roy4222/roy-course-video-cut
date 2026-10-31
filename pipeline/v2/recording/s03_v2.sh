. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "關卡2：工程師學乖了，密碼不再明文"
run 'echo woof-2026-guide | ./dog_unlock_v2'
run 'strings dog_unlock_v2 | grep -iE "woof|code|ACCESS|heel"' 3
say "strings 只看到訊息，看不到密碼。換第二招：objdump 反組譯"
run 'objdump -d --no-show-raw-insn -M intel dog_unlock_v2 | grep -A40 "<check_code>:" | head -42' 6
say "四個線索：0xd(=13)、strlen、xor 0x4a、secret 陣列"
run 'objdump -d -M intel dog_unlock_v2 | awk "/<check_code>:/,/<main>:/" | grep -E ",0xd$|strlen|xor .*0x4a|<secret>"' 5

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "第二題：-O2 最佳化 + strip 拿掉所有函式名字"
run 'gcc -O2 -s -o mystery_dog dog_unlock_v2.c && nm mystery_dog' 2.5
say "代理人第 1 步：找可疑字串"
run 'rea search mystery_dog ACCESS --provider ghidra --format json | nr' 2.5
say "第 2 步：誰用到 ACCESS GRANTED？（交叉引用 xrefs）"
run 'rea xrefs mystery_dog 0x102030 --provider ghidra --format json | nr' 2.5
say "第 3 步：反編譯那個位置 —— 名字沒了，只剩 FUN_"
run 'rea decompile mystery_dog 0x101102 --provider ghidra --format json | nr' 4
say "第 4 步：追進 FUN_00101220"
run 'rea decompile mystery_dog 0x101220 --provider ghidra --format json | nr' 4
say "第 5 步：讀 DAT_00102060 的 13 個位元組"
run 'rea read-bytes mystery_dog 0x102060 --length 13 --provider ghidra --format json | nr bytes_hex' 2.5
run 'python3 -c "print(bytes(b ^ 0x4a for b in bytes.fromhex(\"39233e67393e2b3367222f2f26\")).decode())"' 2
run 'echo sit-stay-heel | ./mystery_dog' 3

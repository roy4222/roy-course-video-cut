. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "第三題：同一支程式，用 UPX 壓縮殼包起來"
run 'ls -l mystery_dog mystery_dog_packed && echo sit-stay-heel | ./mystery_dog_packed' 2.5
say "程式照跑，但 REA + Ghidra 找不到任何字串"
run 'rea search mystery_dog_packed ACCESS --provider ghidra --format json | nr' 2.5
say "REA 的熵值工具：數字越接近 8，越像壓縮或加密"
run 'for f in mystery_dog mystery_dog_packed; do echo -n "$f  "; rea inspect-byte-entropy $f --format json | nr file_entropy; done' 3
run 'rea inspect-byte-entropy mystery_dog_packed --format json | nr limits 1' 3
say "REA 不會自動脫殼。人來判斷：這是 UPX，用 upx -d"
run 'cp mystery_dog_packed /tmp/unpacked && upx -q -d /tmp/unpacked >/dev/null && rea search /tmp/unpacked ACCESS --provider ghidra --format json | nr' 3

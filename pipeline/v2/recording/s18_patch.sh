. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "修補長什麼樣？打開 brotli 原始碼（MIT 授權、公開）"
runp 'cd brotli && git log -1 --format="%h  %ad  %an%n    %s" --date=short 0ed4268' 3
say "注意日期：2 月就修了，10 月才公開成 CVE"
runp 'git show 0ed4268 -- c/include/brotli/decode.h | grep -E "^[-+] " ' 3.5
say "原本保留不用的 −17，變成新的錯誤碼：BLOCK_SWITCH 格式錯"
runp "git show 0ed4268 -- c/dec/decode.c | grep -E '^[-+].*(BROTLI_BOOL|BrotliDecoderErrorCode DecodeBlockTypeAndLength|ERROR_FORMAT_BLOCK_SWITCH|return BROTLI_FALSE)' | head -6" 4
say "以前：壞資料 → 回「假」→ 被當成「再給我多一點」"
say "現在：壞資料 → 直接回「格式錯誤」→ 停"
say "同一個修補，10/21 才被搬進正式版 v1.2.1"
runp 'git log --format="%h %ad %s" --date=short v1.2.0..v1.2.1' 3.5
runp 'git show -s --format=%b b418fa8 | grep cherry' 3

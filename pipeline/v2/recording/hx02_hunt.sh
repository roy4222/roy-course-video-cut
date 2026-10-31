. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "玩具程式：FenrisOS 語音指令封包解析器（自己寫的、故意留洞）"
runp 'grep -n -E "struct cmd|len  =|memcpy|speed_limit = 1" fenris_cmd.c' 2.5
say "AI 找洞的第一步也是『讀』：REA + Ghidra 反編譯 parse_packet（事先跑好，約 29 秒）"
runp 'python3 -c "import json;print(json.load(open(\"dec.json\"))[\"normalized_result\"])" | grep -E -A5 "bVar2 = buf"' 3
say "假說：len 最大 255，text 只有 16 格 → 會寫過頭"
say "驗證 1：正常封包（長度 5）"
runp 'xxd pkt_ok.bin; ./fenris_cmd < pkt_ok.bin' 2
say "驗證 2：長度說 20，多出的 4 byte 剛好落在 speed_limit"
runp 'xxd pkt_speed.bin; ./fenris_cmd < pkt_speed.bin' 3
say "導盲限速 1 m/s → 被一個封包改成 9。再用 ASan 拿證據："
runp './fenris_cmd_asan < pkt_long.bin 2>&1 | grep -E "ERROR|WRITE|in parse_packet" | cut -c1-110' 3
say "對照組：不讀程式、只亂丟封包的 fuzz"
runp 'python3 fuzz.py' 2.5
say "修補：先檢查長度。同一個攻擊封包再丟一次："
runp 'grep -n "修補" fenris_cmd_fixed.c | cut -c1-100; ./fenris_cmd_fixed < pkt_long.bin' 3

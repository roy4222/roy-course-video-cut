. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "真實世界：Wi-Fi 名稱（SSID）塞進固定大小的緩衝區"
runp 'cat overflow_asan.c' 3
runp 'gcc -o ssid overflow_asan.c && ./ssid home' 2
printf "${PS_COLOR}roy@lab${RST}:\033[1;34m~/lab/c\033[0m\$ "; type_out './ssid AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'; sleep 0.4; printf '\n'; sh -c './ssid AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'; sleep 2.5
say "Segmentation fault：程式當場倒下。機器狗上就是服務掛掉"
say "神器：AddressSanitizer，編譯時加一個參數"
runp 'gcc -g -fsanitize=address -o ssid_asan overflow_asan.c' 1
runp './ssid_asan AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA 2>&1 | head -6' 4
say "直接告訴你：stack-buffer-overflow、寫了幾 bytes、在第 5 行"

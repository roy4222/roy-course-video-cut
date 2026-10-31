. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/c
say "玩具程式（我自己寫的）：App 傳 Wi-Fi 名稱 → 機器人用 shell 套用"
runp 'sed -n "4,10p" wifi_setup.c' 4
runp 'gcc -o wifi_setup wifi_setup.c && ./wifi_setup "HomeWiFi"' 2.5
say "如果名稱裡藏了引號和分號呢？shell 會把後半段當成新指令"
runp "./wifi_setup 'HomeWiFi\"; whoami; echo \"'" 3
say "多跑了一個 whoami。設定 Wi-Fi 的服務常以 root 執行……"
runp "sudo ./wifi_setup 'HomeWiFi\"; whoami; echo \"'" 3.5
say "root。這類錯誤叫命令注入（CWE-78）"
say "修法：白名單檢查 + 不經過 shell"
runp 'gcc -o wifi_setup_fixed wifi_setup_fixed.c'
runp "./wifi_setup_fixed 'HomeWiFi\"; whoami; echo \"'" 2.5
runp "./wifi_setup_fixed 'Home_WiFi-5G'" 3

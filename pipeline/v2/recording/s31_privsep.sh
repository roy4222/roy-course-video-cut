. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec31; echo "speed=0" > hw/motor
say "同一隻玩具狗，兩種蓋法。先看輸入：一個正常指令、一個壞封包"
runp 'cat input.txt' 2
say "蓋法一：全部塞在同一個行程——解析、金鑰、馬達"
runp 'python3 dog_mono.py < input.txt; cat hw/motor' 4
say "解析器一被控制，金鑰外洩、馬達被設成 9.9：整隻狗都丟了"
echo "speed=0" > hw/motor
say "蓋法二：權限分離。網路行程關進沙箱，馬達行程在外面"
runp 'cat run_split.sh | tail -5' 4
runp 'grep -n "MAX\|fullmatch\|STOP" motor_part.py' 3
say "兩個行程之間只有一條管子，只准講 MOVE 跟 STOP"
runp './run_split.sh < input.txt; cat hw/motor' 4
say "一樣被控制，但它看不到金鑰、摸不到馬達，亂講話也被拒絕"

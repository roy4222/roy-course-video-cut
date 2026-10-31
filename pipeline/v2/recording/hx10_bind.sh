. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/hx10; B=$SEC_LAB/hx10/bin
say "實驗 1：同一個玩具網頁服務，綁兩種位址（全程只在本機）"
say "先綁 0.0.0.0：意思是「所有網路卡都接」"
runp "$B/toyapp toy_app.py 0.0.0.0 8710 &" 1
runp "ss -tlnp 'sport = :8710'" 3
say "0.0.0.0＝區網、甚至路由器轉發進來的人都敲得到"
runp "kill %1; sleep 0.3" 0.8
say "改綁 127.0.0.1：只有這台電腦自己能連"
runp "$B/toyapp toy_app.py 127.0.0.1 8710 &" 1
runp "ss -tlnp 'sport = :8710'" 3
runp "curl -s http://127.0.0.1:8710/" 2
say "這就是 Tunnel 前面的第一步：App 只聽 127.0.0.1"
runp "kill %1" 1

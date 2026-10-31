. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/hx10; B=$SEC_LAB/hx10/bin
say "實驗 2：只往外撥的通道（outbound-only）"
runp "./cloudflared --version" 1.5
say "真的 quick tunnel 要連 Cloudflare；這台實驗機的網路擋住了"
say "所以用三個小程式在本機模擬，全部只用 127.0.0.1"
runp "$B/toyapp toy_app.py 127.0.0.1 8710 &" 0.6
runp "$B/edge fake_edge.py &" 0.6
say "edge 扮演 Cloudflare；cloudflared-sim 扮演你家的 cloudflared"
runp "$B/cloudflared-sim connector.py 8710 &" 1.5
say "誰在「聽」？（LISTEN）"
runp "ss -tlnp | grep -E 'toyapp|edge|cloudflared' | awk '{print \$4, \$6}'" 3
say "cloudflared-sim 沒有在聽任何埠，它只是撥出去"
runp "ss -tnp | grep cloudflared-sim | awk '{print \$1, \$4, \"->\", \$5}'" 3
say "訪客連到 edge，請求順著那條撥出去的線回到 App"
runp "curl -s http://127.0.0.1:8443/" 2.5
say "你家路由器：0 個轉發埠。門沒開，但服務送得出去"
runp "kill %1 %2 %3" 1

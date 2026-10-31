. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "真實世界：Unitree 官方公開的 Go2 SDK（BSD-3 授權）"
run 'ls -lh sdk/ && file sdk/libunitree_sdk2.a' 2.5
say "nm：列出函式庫裡有名字的函式（-C 把 C++ 名字翻成人話）"
run 'nm -C sdk/libunitree_sdk2.a 2>/dev/null | grep " T .*go2::SportClient::" | cut -c20- | head -24' 6
say "沒看文件，就知道 Go2 能 FrontPounce、WalkUpright……"
run 'nm -C sdk/libunitree_sdk2.a 2>/dev/null | grep -c " T "' 2.5
say "1445 個對外函式 = 一張地圖。逆向的第一步永遠是：先畫地圖"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "實驗：自己的玩具網站（127.0.0.1），載入一支『效能監測』腳本"
runp 'grep -o "<script.*" site/sri.html | fold -w 110'
say "integrity = 這支腳本內容的指紋（SHA-384）。自己算一次："
runp 'openssl dgst -sha384 -binary cdn/rum.js | openssl base64 -A; echo' 2
say "正常情況：瀏覽器比對指紋相符 → 腳本照常執行"
runp 'bash check.sh sri.html' 1.5
say "模擬：監測供應商被入侵，同一個網址、內容被換掉"
runp 'cp rum_evil.js cdn/rum.js; cat cdn/rum.js' 2
say "A 網頁：沒有 integrity（只信網址）"
runp 'bash check.sh plain.html' 2
say "B 網頁：有 integrity（信指紋）"
runp 'bash check.sh sri.html' 2.5
say "指紋不符 → 瀏覽器拒絕執行。換掉的腳本一行都沒跑"
runp 'cp rum_clean.js cdn/rum.js' 1

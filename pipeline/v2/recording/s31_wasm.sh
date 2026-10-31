. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
cd $SEC_LAB/sec31
say "另一種沙箱：不靠作業系統，靠編譯器和執行環境——WebAssembly"
runp 'sed -n "4,9p" wasm_box.py' 3
say "這個模組只有 64 KiB 自己的記憶體。我們叫它往不同位址寫"
runp '../go2re/.venv/bin/python wasm_box.py' 4
say "寫出界不會蓋到主程式，直接被攔下：這就是軟體錯誤隔離的想法"

. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "同一個函式丟進 Ghidra 12.1.4（headless 模式）反編譯"
run 'ar t unitree_sdk2/lib/x86_64/libunitree_sdk2.a | wc -l; ls -l sdkobj/sport_client_go2.o | cut -d" " -f5-' 2.5
run 'export JAVA_HOME=$JAVA_HOME; $GHIDRA_INSTALL_DIR/support/analyzeHeadless ghproj p -import sdkobj/sport_client_go2.o -scriptPath ghidra_scripts -postScript DecompHello.java Hello -deleteProject 2>&1 | sed -n "/=== /,/^}/p" | grep -v "^INFO\|^$"' 6
say "Client::Call( 0x3f8 = 1016 )：官方函式庫送的，就是社群表上的 Hello"
say "字串也在：rt/api/、/request、Request denied by lease"
run 'strings sdkobj/sport_client_go2.o | grep -E "^rt/api/$|^/request$|lease|^sport$"' 3

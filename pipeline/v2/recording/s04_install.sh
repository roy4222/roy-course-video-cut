. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "REA 是什麼？npm 上的套件 rea-agents，裝起來就一行"
run 'rea --version'
say "先跑健康檢查 doctor。我一開始裝了最新的 Ghidra 12.2……"
run 'GHIDRA_INSTALL_DIR=$GHIDRA_REJECTED rea doctor 2>&1 | grep -A4 "name: ghidra-version"' 3
say "被拒絕：REA 只認它驗證過的 12.1.x。換成 12.1.4"
run 'rea doctor 2>&1 | grep -A3 -E "name: (ghidra-version|ghidra-java|ghidra-native_decompiler)"' 4
say "它對 AI 代理人開放多少個工具？用 MCP 問它"
run 'python3 mcp_list.py' 5

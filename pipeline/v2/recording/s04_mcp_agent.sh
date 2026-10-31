. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "代理人實際看到的是什麼？直接看 MCP 對話"
say "（呼叫順序由腳本模擬；實際使用時由 AI 代理人自己決定）"
run 'python3 mcp_agent_trace.py mystery_dog' 6

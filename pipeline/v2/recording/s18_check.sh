. "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/env.sh"
say "現場挑戰：我這台機器有沒有中？（只查自己的機器）"
runp 'node --version' 1.5
say "Node 公告：修好的版本是 22.23.4 / 24.22.1 / 26.12.1"
runp "node -p 'process.versions.brotli'" 2.5
say "咦？Node 已更新，但內建 brotli 還說自己是 1.2.0"
runp 'curl -s https://raw.githubusercontent.com/nodejs/node/v24.22.1/deps/brotli/c/common/version.h | grep -E "define BROTLI_VERSION_(MAJOR|MINOR|PATCH)"' 3
say "版本號沒改。那就直接找「修補留下的指紋」"
runp "node -p 'require(\"zlib\").constants.BROTLI_DECODER_ERROR_FORMAT_BLOCK_SWITCH'" 3
say "-17 = 有新錯誤碼 = 修補在；舊版會印 undefined"
say "系統套件：交給發行版的安全公告來判斷"
runp "dpkg-query -W -f='\${Package} \${Version}\n' libbrotli1" 2.5
say "Debian 追蹤頁：trixie (security) 修在 1.1.0-2+deb13u1"
say "最後一步：舊程式還在記憶體裡跑舊版嗎？"
runp "grep -l 'libbrotlidec.*(deleted)' /proc/[0-9]*/maps 2>/dev/null | wc -l" 3
say "0 = 沒有程式還掛著已刪除的舊版函式庫"

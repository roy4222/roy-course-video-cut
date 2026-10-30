#!/usr/bin/env bash
# 下載 Noto Sans CJK TC，轉成 windows-kit/assets/fonts/fonts.css 要用的 woff2。
# 官方來源：https://github.com/notofonts/noto-cjk （SIL Open Font License 1.1）
# 釘選發行檔：Sans2.004 / 09_NotoSansCJKtc.zip
# 不會把字型 commit 進 git。可以重複執行。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/windows-kit/assets/fonts"
LIC="$ROOT/windows-kit/licenses/NotoSansCJK-OFL.txt"
ZIP_URL="https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/09_NotoSansCJKtc.zip"
LIC_URL="https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/LICENSE"
REG="$DEST/NotoSansCJKtc-Regular.woff2"
BOLD="$DEST/NotoSansCJKtc-Bold.woff2"

mkdir -p "$DEST" "$(dirname "$LIC")"

if [[ ! -s "$LIC" ]]; then
  echo "下載授權 $LIC_URL"
  curl -fsSL "$LIC_URL" -o "$LIC"
fi

if [[ -s "$REG" && -s "$BOLD" ]]; then
  echo "字型已經在 $DEST"
  ls -lh "$REG" "$BOLD"
  exit 0
fi

PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [[ -z "$PY" ]]; then
  echo "需要 Python 3，才能把 otf 轉成 woff2。"
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

if ! "$PY" -c "import fontTools, brotli" >/dev/null 2>&1; then
  echo "安裝 fonttools 與 brotli（只用來轉檔，不會改系統字型）。"
  if ! "$PY" -m pip install --user "fonttools>=4.40" "brotli>=1.0"; then
    "$PY" -m venv "$TMP/venv"
    "$TMP/venv/bin/python" -m pip install "fonttools>=4.40" "brotli>=1.0"
    PY="$TMP/venv/bin/python"
  fi
fi
echo "下載官方 Noto Sans CJK TC（約 90 MB）"
echo "  $ZIP_URL"
curl -fL --retry 3 -o "$TMP/noto.zip" "$ZIP_URL"

echo "取出 Regular / Bold，轉成 woff2 …"
"$PY" - "$TMP/noto.zip" "$DEST" <<'PY'
import sys
from pathlib import Path
from zipfile import ZipFile
from fontTools.ttLib import TTFont

zip_path, dest = Path(sys.argv[1]), Path(sys.argv[2])
want = {
    "NotoSansCJKtc-Regular.otf": dest / "NotoSansCJKtc-Regular.woff2",
    "NotoSansCJKtc-Bold.otf": dest / "NotoSansCJKtc-Bold.woff2",
}
found = {}
with ZipFile(zip_path) as z:
    for info in z.infolist():
        base = info.filename.replace("\\", "/").rsplit("/", 1)[-1]
        if base in want and base not in found:
            found[base] = z.read(info)
missing = [name for name in want if name not in found]
if missing:
    raise SystemExit("壓縮檔裡找不到：" + ", ".join(missing))
for otf_name, woff in want.items():
    tmp = dest / (otf_name + ".tmp")
    tmp.write_bytes(found[otf_name])
    font = TTFont(str(tmp), recalcBBoxes=False, recalcTimestamp=False)
    font.flavor = "woff2"
    font.save(str(woff))
    font.close()
    tmp.unlink()
    size = woff.stat().st_size
    if size < 1_000_000:
        raise SystemExit(f"{woff.name} 只有 {size} bytes，轉換可能失敗")
    print(f"  {woff.name}  {size/1024/1024:.1f} MB")
PY

echo "完成。這兩個 woff2 已在 .gitignore 裡，請不要 commit。"
echo "授權：$LIC"

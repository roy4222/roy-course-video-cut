#!/usr/bin/env bash
# 取得 lemo-opuscar，並停在本專案用過的那個 commit。
# 上游：https://github.com/lemomo-ai/lemo-opuscar （MIT）
# 不會把上游程式 commit 進這個倉庫。可以重複執行。
set -euo pipefail

PIN="f17136060781a0068a7951245a3aa7835a7230de"
URL="https://github.com/lemomo-ai/lemo-opuscar.git"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${LEMO_OPUSCAR:-$ROOT/third_party/lemo-opuscar}"

mkdir -p "$(dirname "$DEST")"
if [[ ! -d "$DEST/.git" ]]; then
  rm -rf "$DEST"
  git init "$DEST"
  git -C "$DEST" remote add origin "$URL"
fi
echo "抓取 commit $PIN"
git -C "$DEST" fetch --depth 1 origin "$PIN"
git -C "$DEST" checkout --detach FETCH_HEAD

OVERLAY="$ROOT/legacy/lemo_overlay/core/tts"
if [[ -d "$OVERLAY" ]]; then
  mkdir -p "$DEST/core/tts"
  cp -f "$OVERLAY"/*.py "$DEST/core/tts/"
  echo "已把 legacy/lemo_overlay/core/tts/*.py 複製進 checkout（這是我們加的 TTS，不是上游的檔）。"
fi

echo
echo "lemo-opuscar 在：$DEST"
echo "commit：$(git -C "$DEST" rev-parse HEAD)"
echo "舊管線若要叫它： export LEMO_OPUSCAR=\"$DEST\""
echo "第一次使用請在該資料夾執行： npm ci"
echo "授權：上游 MIT。windows-kit/render 裡的修改版另有一份全文：windows-kit/licenses/lemo-opuscar-MIT.txt"

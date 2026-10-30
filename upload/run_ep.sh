#!/bin/bash
# usage: run_ep.sh NN [--dry-run]
# Paths default to the Mac layout used on 2026-10-30. Override with YT_EDITOR_ROOT, YT_INBOX, YT_UPLOAD_PY.
set -e
EP=$1; shift
ROOT="${YT_EDITOR_ROOT:-$HOME/Documents/roy-ai-editor}"
IN="${YT_INBOX:-$ROOT/yt_inbox}"
UPLOAD_PY="${YT_UPLOAD_PY:-$HOME/.claude/skills/roy-upload-video/scripts/upload.py}"
cd "$ROOT"
FILE=$(python3 -c "import json;print(json.load(open('$IN/meta.json'))['$EP']['file'])")
TITLE=$(python3 -c "import json;print(json.load(open('$IN/meta.json'))['$EP']['title'])")
TAGS=$(python3 -c "import json;print(json.load(open('$IN/meta.json'))['$EP']['tags'])")
if echo "$TAGS$TITLE" | grep -q "輔大\|資管"; then echo "BLOCKED: 輔大資管 in tags/title"; exit 3; fi
if grep -q "輔大\|資管" "$IN/ep${EP}_desc.txt"; then echo "BLOCKED: 輔大資管 in desc"; exit 3; fi
uv run python "$UPLOAD_PY" --file "$IN/$FILE" --title "$TITLE" --description-file "$IN/ep${EP}_desc.txt" --tags "$TAGS" --lang zh-TW --synthetic yes "$@"

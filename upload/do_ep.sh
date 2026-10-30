#!/bin/bash
# usage: do_ep.sh NN  -> dry-run, then real upload, delete mp4 on success
# YT_EDITOR_ROOT / YT_INBOX override the Mac inbox. run_ep.sh is the copy next to this file.
EP=$1
ROOT="${YT_EDITOR_ROOT:-$HOME/Documents/roy-ai-editor}"
IN="${YT_INBOX:-$ROOT/yt_inbox}"
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$IN"
FILE=$(python3 -c "import json;print(json.load(open('meta.json'))['$EP']['file'])")
DRY=$(bash "$HERE/run_ep.sh" $EP --dry-run 2>&1); echo "DRY: $(echo "$DRY" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d["status"],d.get("url",""),d["metadata"]["title"] if "metadata" in d else "")' 2>&1 || echo "$DRY" | tail -5)"
if echo "$DRY" | grep -q '"already_uploaded"'; then echo "$DRY"; rm -f "$FILE"; exit 0; fi
echo "$DRY" | grep -q '"dry_run"' || { echo "$DRY" | tail -20; exit 2; }
OUT=$(bash "$HERE/run_ep.sh" $EP 2>&1); echo "$OUT" | tail -5
echo "$OUT" | grep -q '"status": "uploaded"' && rm -f "$FILE" && echo "deleted $FILE"

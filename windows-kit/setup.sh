#!/usr/bin/env bash
# ml-video-kit setup for Linux / macOS. Safe to run again (idempotent), no prompts.
#   bash setup.sh [--cuda] [--no-models] [--python 3.11]
set -euo pipefail
cd "$(dirname "$0")"
KIT="$(pwd)"; CUDA=0; MODELS=1; PYV=3.11
while [ $# -gt 0 ]; do case "$1" in
  --cuda) CUDA=1;; --no-models) MODELS=0;; --python) PYV="$2"; shift;;
  *) echo "unknown option $1"; exit 2;; esac; shift; done
say() { printf '\n==> %s\n' "$*"; }
die() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

say "1/6 uv (Python manager)"
if ! command -v uv >/dev/null 2>&1; then
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
uv --version

say "2/6 Python $PYV venv (.venv) + packages"
[ -x .venv/bin/python ] || uv venv --python "$PYV" .venv
uv pip install --python .venv/bin/python -r requirements.txt
[ "$CUDA" = 1 ] && uv pip install --python .venv/bin/python -r requirements-cuda.txt
.venv/bin/python -c "import faster_whisper, soundfile, numpy, opencc; print('python deps OK')"

say "3/6 Node.js + playwright-core"
command -v node >/dev/null 2>&1 || die "Node.js 18+ not found. Linux: sudo apt install nodejs npm (or https://nodejs.org); macOS: brew install node"
NODE_MAJOR=$(node -p 'process.versions.node.split(".")[0]')
[ "$NODE_MAJOR" -ge 18 ] || die "Node.js $(node -v) is too old; need 18+"
npm install --no-audit --no-fund

say "4/6 Chromium (headless shell) into .browsers/"
export PLAYWRIGHT_BROWSERS_PATH="$KIT/.browsers"
node node_modules/playwright-core/cli.js install --no-remove chromium-headless-shell
if [ "$(uname)" = Linux ]; then
  echo "(if Chromium fails to start with missing .so libraries: sudo node node_modules/playwright-core/cli.js install-deps chromium-headless-shell)"
fi

say "5/6 ffmpeg"
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  ffmpeg -hide_banner -version | head -1
  if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q h264_nvenc && command -v nvidia-smi >/dev/null 2>&1; then
    echo "NVIDIA GPU + h264_nvenc available: you can add --nvenc"; fi
else
  echo "ffmpeg NOT found. Install it, then run setup again:"
  echo "  Debian/Ubuntu: sudo apt install -y ffmpeg"
  echo "  Fedora:        sudo dnf install -y ffmpeg"
  echo "  macOS:         brew install ffmpeg"
  exit 1
fi

say "6/6 Whisper model + .env"
export HF_HOME="$KIT/.cache/huggingface"
if [ "$MODELS" = 1 ]; then
  .venv/bin/python -c "from faster_whisper import WhisperModel; WhisperModel('small', device='cpu', compute_type='float32'); print('whisper small cached')"
fi
[ -f .env ] || { cp .env.example .env; echo "created .env: put your OPENROUTER_API_KEY in it"; }
chmod +x make_episode.sh 2>/dev/null || true
CPU=$(getconf _NPROCESSORS_ONLN 2>/dev/null || echo 4)
echo
echo "Setup finished. Smoke test (no API key needed, uses the bundled sample voice):"
echo "  ./make_episode.sh episodes/sample"
echo "Auto render workers on this machine: $(.venv/bin/python -c 'import make_episode as m; print(m.auto_workers())')  (CPU threads: $CPU)"

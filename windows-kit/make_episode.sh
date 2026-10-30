#!/usr/bin/env sh
# Linux/macOS wrapper: ./make_episode.sh <episode_dir> [steps...] [--workers N] [--nvenc]
D="$(cd "$(dirname "$0")" && pwd)"
exec "$D/.venv/bin/python" "$D/make_episode.py" "$@"

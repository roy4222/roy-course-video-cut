"""Drop leading and trailing near-black JPEGs in film_media/rec/*, renumber, update n= in build.py.

md2build_v2.py calls this after it extracts recording frames. The 2026-10-31 export
invoked the script but did not include it. Behavior here follows the render notes:
terminal grabs often start with a few black frames and end with a few more, and
freezing the last frame then froze on black.

usage: python3 trim_dark_tail.py <episode_dir> <film_media_dir>
"""
import re, sys, subprocess
from pathlib import Path

# #0d1117 terminal background is about YAVG 16. Empty grab frames sit near 0.
THRESH = 8.0
MAX_DROP = 8
KEEP_AT_LEAST = 2


def yavg(path):
    """Mean luma, 0–255. signalstats' log line is not printed by every ffmpeg build."""
    proc = subprocess.run(
        ['ffmpeg', '-loglevel', 'error', '-i', str(path), '-f', 'rawvideo', '-pix_fmt', 'gray', '-'],
        capture_output=True)
    data = proc.stdout
    if proc.returncode != 0 or not data:
        return None
    return sum(data) / len(data)


def frame_list(rec_dir):
    frames = []
    for p in rec_dir.glob('*.jpg'):
        try:
            n = int(p.stem)
        except ValueError:
            continue
        frames.append((n, p))
    frames.sort()
    return [p for _, p in frames]


def trim_one(rec_dir, build_text):
    frames = frame_list(rec_dir)
    if len(frames) < KEEP_AT_LEAST + 1:
        print(rec_dir.name, 'skip short', len(frames))
        return build_text, False
    bright = [yavg(p) for p in frames]
    lead = 0
    while (lead < len(frames) - KEEP_AT_LEAST and lead < MAX_DROP
           and bright[lead] is not None and bright[lead] < THRESH):
        lead += 1
    tail = 0
    while (tail < len(frames) - lead - KEEP_AT_LEAST and tail < MAX_DROP
           and bright[-1 - tail] is not None and bright[-1 - tail] < THRESH):
        tail += 1
    if lead == 0 and tail == 0:
        print(rec_dir.name, 'no dark ends', 'n', len(frames))
        return build_text, False
    name = rec_dir.name
    pat = re.compile(r"(dir='rec/" + re.escape(name) + r"', n=)(\d+)")
    if not pat.search(build_text):
        print(rec_dir.name, 'dark ends found but build.py has no n= for this rec; left frames alone', file=sys.stderr)
        return build_text, False
    kept = frames[lead:len(frames) - tail if tail else len(frames)]
    tmp = rec_dir / '.trimtmp'
    tmp.mkdir(exist_ok=False)
    for i, p in enumerate(kept, 1):
        p.rename(tmp / f'{i:04d}.jpg')
    for p in frames:
        if p.exists():
            p.unlink()
    for p in sorted(tmp.glob('*.jpg')):
        p.rename(rec_dir / p.name)
    tmp.rmdir()
    new_text, nsub = pat.subn(lambda m: m.group(1) + str(len(kept)), build_text, count=1)
    print(rec_dir.name, 'dropped', lead, 'head', tail, 'tail', 'n', len(frames), '->', len(kept))
    return new_text, nsub == 1


def main():
    if len(sys.argv) != 3:
        print('usage: trim_dark_tail.py <episode_dir> <film_media_dir>', file=sys.stderr)
        return 2
    ep, media = Path(sys.argv[1]), Path(sys.argv[2])
    rec_root = media / 'rec'
    if not rec_root.is_dir():
        print('no rec dir')
        return 0
    build = ep / 'build.py'
    text = build.read_text(encoding='utf-8') if build.exists() else ''
    changed = False
    for d in sorted(p for p in rec_root.iterdir() if p.is_dir() and p.name != '.trimtmp'):
        text, did = trim_one(d, text)
        changed = changed or did
    if changed and build.exists():
        build.write_text(text, encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())

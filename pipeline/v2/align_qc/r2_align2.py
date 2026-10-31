"""Renderer2: per-line Whisper forced alignment on the REAL TTS wavs -> fine cues (<=18 chars).
Writes cues_fine.json, injects window.SUBS into film/timeline.js (burned-in subs), writes epNN.srt.
usage: python r2_align.py <episode_dir>   (run with the kit venv; cwd anywhere)"""
import sys, os, json, re, time, difflib
KIT = os.environ.get('KIT') or os.path.dirname(os.path.abspath(sys.executable)).rsplit('/.venv', 1)[0]
sys.path.insert(0, KIT)
from kit.force_srt import align_chars, _norm, write_srt, cues_from_line
import math
PUN = set('，。！？；：、,.!?;:')
def _split_long(c, mx):
    # balanced split of a clause with no punctuation; never cut inside an ASCII word/number
    k = math.ceil(len(c) / mx); out = []
    while c:
        if len(c) <= mx: out.append(c); break
        tgt = math.ceil(len(c) / k); k -= 1
        cands = [j for j in range(max(2, tgt - 4), min(len(c) - 1, mx) + 1)
                 if not (c[j - 1].isascii() and c[j - 1].isalnum() and c[j].isascii() and c[j].isalnum())]
        j = min(cands, key=lambda j: (abs(j - tgt) + (0 if c[j - 1] == ' ' or c[j] == ' ' else 0.5))) if cands else min(mx, len(c))
        out.append(c[:j].strip()); c = c[j:].strip()
    return [o for o in out if o]
def chunk_text(text, mx=18):
    text = text.strip(); cl = []; buf = ''
    for ch in text:
        buf += ch
        if ch in PUN: cl.append(buf); buf = ''
    if buf.strip(): cl.append(buf)
    cl = [c.strip() for c in cl if c.strip()]
    out = []
    for c in cl:
        if len(c) > mx:
            out.extend(_split_long(c, mx))
        elif out and len(out[-1]) + len(c) <= mx and (len(c) <= 4 or len(out[-1]) <= 6):
            out[-1] += c
        elif out and len(out[-1]) + len(c) <= mx and len(out[-1]) + len(c) <= 14:
            out[-1] += c
        else:
            out.append(c)
    # glue punctuation-only pieces
    res = []
    for c in out:
        if res and not any(ch.isalnum() for ch in c) and len(res[-1]) + len(c) <= mx: res[-1] += c
        else: res.append(c)
    return res

import opencc, subprocess
from faster_whisper import WhisperModel
cc = opencc.OpenCC('s2t')
d = os.path.abspath(sys.argv[1]); os.chdir(d)
tl = open('film/timeline.js', encoding='utf-8').read()
L = json.loads(tl.split('window.LINES=')[1].split(';\nwindow.SCENES')[0])
meta = json.load(open('meta.json', encoding='utf-8')); N = int(re.match(r'\d+', str(meta['num'])).group())
os.environ.setdefault('HF_HOME', os.path.join(KIT, '.cache', 'huggingface'))
t_start = time.time()
# continuous narration exactly as it will be heard: place every voice line on the timeline (same as the kit's mix step)
import numpy as np, soundfile as sf
DUR = float(tl.split('window.DUR=')[1].split(';')[0]); sr = 24000
buf = np.zeros(int(DUR * sr) + sr, dtype=np.float32)
for l in L:
    a, r = sf.read(f"voice/{l['id']}.wav", dtype='float32')
    if a.ndim > 1: a = a.mean(axis=1)
    i0 = int(l['t0'] * sr); buf[i0:i0 + len(a)] += a[:len(buf) - i0]
os.makedirs('qc', exist_ok=True); sf.write('qc/r2_mix.wav', buf, sr)
m = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=int(os.environ.get('R2_THREADS', '4')))
segs, _ = m.transcribe('qc/r2_mix.wav', language='zh', word_timestamps=True, vad_filter=True,
                       condition_on_previous_text=False, initial_prompt='以下是繁體中文的資訊安全課程旁白。')
hyp, hs_, he_ = [], [], []
for sg in segs:
    for w in (sg.words or []):
        cs = _norm(w.word, cc); ws, we = float(w.start), float(w.end)
        for k, c in enumerate(cs):
            hyp.append(c); hs_.append(ws + (we - ws) * k / max(1, len(cs))); he_.append(ws + (we - ws) * (k + 1) / max(1, len(cs)))
fine = []; stats = []
for i, l in enumerate(L):
    text = l['text']; t0, t1 = l['t0'], l['t1']
    nxt = L[i + 1]['t0'] if i + 1 < len(L) else t1 + 2.0
    chunks = chunk_text(text, 18)
    ref = _norm(text, cc)
    w0, w1 = t0 - 3.0, t1 + 3.0
    J = [j for j in range(len(hyp)) if w0 <= hs_[j] <= w1]
    sm = difflib.SequenceMatcher(None, ref, [hyp[j] for j in J], autojunk=False)
    st = [None] * len(ref); en = [None] * len(ref)
    for b in sm.get_matching_blocks():
        for k in range(b.size): st[b.a + k] = hs_[J[b.b + k]]; en[b.a + k] = he_[J[b.b + k]]
    cov = sum(x is not None for x in st) / max(1, len(ref))
    # chunk char ranges
    rng = []; idx = 0
    for c in chunks:
        n = len(_norm(c, cc)); rng.append((idx, idx + n)); idx += n
    ok = cov >= 0.6
    starts = []
    if ok:
        for (a, b) in rng:
            v = [st[j] for j in range(a, b) if st[j] is not None]
            # only trust a chunk start if one of its first 3 chars was heard
            v3 = [st[j] for j in range(a, min(b, a + 3)) if st[j] is not None]
            starts.append(min(v3) if v3 else None)
        # interpolate missing starts by char position
        known = [(rng[k][0], s) for k, s in enumerate(starts) if s is not None]
        if not known: ok = False
    if ok:
        for k, s in enumerate(starts):
            if s is None:
                p = rng[k][0]
                lo = max([q for q in known if q[0] < p], default=None, key=lambda q: q[0])
                hi = min([q for q in known if q[0] > p], default=None, key=lambda q: q[0])
                if lo and hi: starts[k] = lo[1] + (hi[1] - lo[1]) * (p - lo[0]) / (hi[0] - lo[0])
                elif lo: starts[k] = lo[1] + (p - lo[0]) * 0.2
                else: starts[k] = hi[1] - (hi[0] - p) * 0.2
        # sanity: monotonic and >=0.08 s per char between chunk starts
        for k in range(1, len(starts)):
            if starts[k] - starts[k - 1] < 0.08 * max(1, rng[k - 1][1] - rng[k - 1][0]): ok = False
        last_end = max([e for e in en if e is not None], default=t1)
    stats.append(dict(id=l['id'], coverage=round(cov, 2), how='whisper-mix' if ok else 'proportional',
                      shift=round(starts[0] - t0, 2) if ok else 0))
    if ok:
        cs = [{'t0': round(max(0.0, s - 0.1), 3), 'text': c} for s, c in zip(starts, chunks)]
        end = min(max(last_end, starts[-1] + 0.5) + 0.35, (nxt if i + 1 < len(L) else DUR) + 1.0)
    else:
        w = [max(1, b - a) for a, b in rng]; tot = sum(w); cs = []; t = t0
        for c, wi in zip(chunks, w):
            cs.append({'t0': round(t, 3), 'text': c}); t += (t1 - t0) * wi / tot
        end = min(t1 + 0.35, nxt - 0.05)
    for k in range(len(cs)):
        cs[k]['t1'] = cs[k + 1]['t0'] if k + 1 < len(cs) else round(end, 3)
    fine.extend(cs)
# global monotonic, min 0.5 s on screen, no overlaps
for k in range(1, len(fine)):
    if fine[k]['t0'] < fine[k - 1]['t0'] + 0.5: fine[k]['t0'] = round(fine[k - 1]['t0'] + 0.5, 3)
for k in range(len(fine) - 1):
    if fine[k]['t1'] > fine[k + 1]['t0'] or fine[k]['t1'] < fine[k]['t0'] + 0.3: fine[k]['t1'] = fine[k + 1]['t0']
json.dump(fine, open('cues_fine.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(stats, open('qc/r2_align_stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
inj = 'window.SUBS=' + json.dumps(fine, ensure_ascii=False) + ';\n'
body = re.sub(r'window\.SUBS=.*?;\n', lambda _: inj, tl, count=1) if 'window.SUBS=' in tl else inj + tl
open('film/timeline.js', 'w', encoding='utf-8', newline='\n').write(body)
write_srt(fine, f'ep{N:02d}.srt')
a = ''.join(''.join(_norm(c['text'], cc)) for c in fine); b = ''.join(''.join(_norm(l['text'], cc)) for l in L)
over = sum(1 for c in fine if len(c['text']) > 18)
sh = [abs(s['shift']) for s in stats if s['how'] != 'proportional']
print(f'[r2_align2] {len(L)} lines -> {len(fine)} cues; whisper-mix {len(sh)}/{len(stats)}; mean cov {sum(s["coverage"] for s in stats)/len(stats):.2f}; '
      f'lines shifted >0.5s {sum(x > 0.5 for x in sh)}; over18 {over}; text_complete {a==b}; {time.time()-t_start:.0f}s')

"""Renderer2: per-line Whisper forced alignment on the REAL TTS wavs -> fine cues (<=18 chars).
Writes cues_fine.json, injects window.SUBS into film/timeline.js (burned-in subs), writes epNN.srt.
usage: python r2_align.py <episode_dir>   (run with the kit venv; cwd anywhere)"""
import sys, os, json, re, time
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

import opencc
from faster_whisper import WhisperModel
cc = opencc.OpenCC('s2t')
d = os.path.abspath(sys.argv[1]); os.chdir(d)
tl = open('film/timeline.js', encoding='utf-8').read()
L = json.loads(tl.split('window.LINES=')[1].split(';\nwindow.SCENES')[0])
meta = json.load(open('meta.json', encoding='utf-8')); N = int(re.match(r'\d+', str(meta['num'])).group())
os.environ.setdefault('HF_HOME', os.path.join(KIT, '.cache', 'huggingface'))
m = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=int(os.environ.get('R2_THREADS', '4')))
fine = []; stats = []; t_start = time.time()
for i, l in enumerate(L):
    text = l['text']; t0, t1 = l['t0'], l['t1']
    nxt = L[i + 1]['t0'] if i + 1 < len(L) else t1 + 2.0
    chunks = chunk_text(text, 18)
    segs, _ = m.transcribe(f"voice/{l['id']}.wav", language='zh', word_timestamps=True, vad_filter=False,
                           condition_on_previous_text=False, initial_prompt='以下是繁體中文的句子。' + text)
    words = [{'word': w.word, 'start': float(w.start), 'end': float(w.end)} for s in segs for w in (s.words or [])]
    hyp = cc.convert(''.join(w['word'] for w in words))
    ok = False
    if words:
        times, match, ref = align_chars(text, words, cc)
        ok = match >= 0.5 and len(times) == sum(len(_norm(c, cc)) for c in chunks)
    stats.append(dict(id=l['id'], match=round(match, 2) if words else 0, how='whisper' if ok else 'proportional', heard=hyp))
    if ok:
        # sanity: every chunk must get plausible speaking time (>=0.09 s per char); else distrust whisper
        idx = 0; starts = []
        for c in chunks:
            n = len(_norm(c, cc)); starts.append(times[idx] if n and idx < len(times) else None); idx += n
        if starts: starts[0] = 0.0
        sts = [x for x in starts if x is not None] + [t1 - t0]
        for k in range(len(sts) - 1):
            seg_chars = max(1, len(_norm(chunks[k], cc))) if k < len(chunks) else 1
            if sts[k + 1] - sts[k] < 0.09 * seg_chars: ok = False; stats[-1]['how'] = 'proportional(sanity)'; break
    if not ok:
        w = [max(1, len(_norm(c, cc))) for c in chunks]; tot = sum(w); cs = []; t = t0
        for c, wi in zip(chunks, w):
            cs.append({'t0': round(t, 3), 'text': c}); t += (t1 - t0) * wi / tot
        for k in range(len(cs)):
            cs[k]['t1'] = cs[k + 1]['t0'] if k + 1 < len(cs) else round(min(t1 + 0.35, nxt - 0.05), 3)
    else:
        cs = []; idx = 0
        for c in chunks:
            n = len(_norm(c, cc))
            st = t0 if not cs else t0 + max(0.0, times[idx] - 0.12) if n else None
            if st is None:  # punctuation-only chunk: glue to previous
                if cs and len(cs[-1]['text']) + len(c) <= 18: cs[-1]['text'] += c
                continue
            cs.append({'t0': round(min(st, t1 - 0.2), 3), 'text': c}); idx += n
        for k in range(len(cs)):
            cs[k]['t1'] = cs[k + 1]['t0'] if k + 1 < len(cs) else round(min(t1 + 0.35, nxt - 0.05), 3)
        # monotonic + min display 0.5s
        for k in range(1, len(cs)):
            if cs[k]['t0'] < cs[k - 1]['t0'] + 0.5:
                cs[k]['t0'] = round(min(cs[k - 1]['t0'] + 0.5, t1 - 0.1), 3); cs[k - 1]['t1'] = cs[k]['t0']
    fine.extend(cs)
for k in range(len(fine) - 1):
    if fine[k]['t1'] > fine[k + 1]['t0']: fine[k]['t1'] = fine[k + 1]['t0']
json.dump(fine, open('cues_fine.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(stats, open('qc/r2_align_stats.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
inj = 'window.SUBS=' + json.dumps(fine, ensure_ascii=False) + ';\n'
body = re.sub(r'window\.SUBS=.*?;\n', lambda _: inj, tl, count=1) if 'window.SUBS=' in tl else inj + tl
open('film/timeline.js', 'w', encoding='utf-8', newline='\n').write(body)
write_srt(fine, f'ep{N:02d}.srt')
# completeness check: fine texts == script lines
a = ''.join(''.join(_norm(c['text'], cc)) for c in fine); b = ''.join(''.join(_norm(l['text'], cc)) for l in L)
over = sum(1 for c in fine if len(c['text']) > 18)
print(f'[r2_align] {len(L)} lines -> {len(fine)} cues; whisper {sum(s["how"]=="whisper" for s in stats)}/{len(stats)}; '
      f'mean match {sum(s["match"] for s in stats)/len(stats):.2f}; over18 {over}; text_complete {a==b}; {time.time()-t_start:.0f}s')

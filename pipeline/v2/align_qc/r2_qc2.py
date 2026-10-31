"""Renderer2 QC v2: Whisper the whole final mp4 once (word timestamps), align the transcript to the subtitle
cue text globally, and for every cue measure whether its words are actually heard while it is on screen.
usage: r2_qc2.py <mp4> <cues_fine.json> <script.json> <out.json>"""
import sys, json, subprocess, difflib, os, statistics
K = os.environ['KIT']; sys.path.insert(0, K)  # v1 windows-kit; see pipeline/v2/config.example.env
os.environ.setdefault('HF_HOME', K + '/.cache/huggingface')
from kit.force_srt import _norm
import opencc; from faster_whisper import WhisperModel
cc = opencc.OpenCC('s2t')
mp4, cf, sj, outp = sys.argv[1:5]
fine = json.load(open(cf, encoding='utf-8')); S = json.load(open(sj, encoding='utf-8'))
wav = '/tmp/r2qc_%d.wav' % os.getpid()
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp4, '-ac', '1', '-ar', '16000', wav], check=True)
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout)
m = WhisperModel('small', device='cpu', compute_type=os.environ.get('R2_CT','float32'), cpu_threads=int(os.environ.get('R2_THREADS', '4')))
segs, _ = m.transcribe(wav, language='zh', word_timestamps=True, vad_filter=True, condition_on_previous_text=False,
                       initial_prompt='以下是繁體中文的資訊安全課程旁白。')
hyp, ht = [], []
for s in segs:
    for w in (s.words or []):
        cs = _norm(w.word, cc)
        for k, c in enumerate(cs):
            hyp.append(c); ht.append(float(w.start) + (float(w.end) - float(w.start)) * (k + 0.5) / max(1, len(cs)))
lines = json.load(open(os.path.join(os.path.dirname(cf), 'cues.json'), encoding='utf-8'))
res = []; tot_ref = tot_heard = 0
for i, c in enumerate(fine):
    # local window: the narration line that contains this cue, +-2.5 s
    L = next((l for l in lines if l['t0'] - 0.05 <= c['t0'] <= l['t1'] + 0.4), None)
    w0, w1 = (L['t0'] - 2.5, L['t1'] + 2.5) if L else (c['t0'] - 3, c['t1'] + 3)
    hj = [j for j, t in enumerate(ht) if w0 <= t <= w1]
    hloc = [hyp[j] for j in hj]; tloc = [ht[j] for j in hj]
    # align the whole line text (so repeated words inside the line map correctly), then pick this cue's chars
    ltext = L['text'] if L else c['text']
    lref = _norm(ltext, cc); cref = _norm(c['text'], cc)
    sm = difflib.SequenceMatcher(None, lref, hloc, autojunk=False)
    lh = [None] * len(lref)
    for b in sm.get_matching_blocks():
        for k in range(b.size): lh[b.a + k] = tloc[b.b + k]
    # locate cue chars inside the line text
    pos = ''.join(lref).find(''.join(cref))
    hs = [h for h in (lh[pos:pos + len(cref)] if pos >= 0 else []) if h is not None]
    inwin = [h for h in hs if c['t0'] - 0.3 <= h <= c['t1'] + 0.3]
    cov = len(hs) / max(1, len(cref)); tot_ref += len(cref); tot_heard += len(hs)
    sync = len(inwin) / len(hs) if len(hs) >= 2 else None
    off = round(min(hs) - c['t0'], 2) if hs else None
    res.append(dict(t0=c['t0'], t1=c['t1'], text=c['text'], coverage=round(cov, 2), sync=None if sync is None else round(sync, 2), start_offset=off))
heard = [1] * tot_heard + [None] * (tot_ref - tot_heard); ref = heard
sy = [r['sync'] for r in res if r['sync'] is not None]
a1 = ''.join(''.join(_norm(c['text'], cc)) for c in fine); b1 = ''.join(''.join(_norm(l['text'], cc)) for l in S)
summ = dict(duration_s=round(dur, 1), duration=f'{int(dur//60)}:{int(dur%60):02d}', cues=len(fine),
            over18=sum(len(c['text']) > 18 for c in fine), max_chars=max(len(c['text']) for c in fine),
            text_complete=(a1 == b1), heard_coverage=round(sum(1 for h in heard if h is not None) / len(ref), 3),
            sync_mean=round(sum(sy) / len(sy), 3), sync_median=statistics.median(sy), cues_checked=len(sy),
            cues_sync_lt_0_6=sum(s < 0.6 for s in sy),
            start_offset_ge_0_9s=sum(1 for r in res if r['start_offset'] is not None and abs(r['start_offset']) >= 0.9 and (r['coverage'] or 0) >= 0.5))
json.dump(dict(summary=summ, transcript=''.join(hyp), cues=res), open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(json.dumps(summ, ensure_ascii=False))
for r in res:
    if r['sync'] is not None and r['sync'] < 0.6: print('OFF', r)
os.remove(wav)

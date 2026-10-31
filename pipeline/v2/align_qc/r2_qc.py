"""Renderer2 QC: per-cue sync on final mp4 vs cues_fine.json. usage: r2_qc.py <mp4> <cues_fine.json> <script.json> <out.json>"""
import sys, json, re, subprocess, difflib, os, numpy as np, soundfile as sf
K = os.environ['KIT']; sys.path.insert(0, K)  # v1 windows-kit; see pipeline/v2/config.example.env
os.environ.setdefault('HF_HOME', K + '/.cache/huggingface')
from kit.force_srt import _norm
import opencc; from faster_whisper import WhisperModel
cc = opencc.OpenCC('s2t')
mp4, cf, sj, outp = sys.argv[1:5]
fine = json.load(open(cf, encoding='utf-8')); S = json.load(open(sj, encoding='utf-8'))
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', mp4, '-ac', '1', '-ar', '16000', '/tmp/r2qc.wav'], check=True)
a, sr = sf.read('/tmp/r2qc.wav', dtype='float32')
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout)
m = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=int(os.environ.get('R2_THREADS', '6')))
res = []
for c in fine:
    pre = 0.4; s0 = max(0, c['t0'] - pre); s1 = min(dur, c['t1'] + 0.2)
    seg = a[int(s0 * sr):int(s1 * sr)]
    segs, _ = m.transcribe(seg, language='zh', word_timestamps=True, vad_filter=False, condition_on_previous_text=False,
                           initial_prompt='以下是繁體中文的句子。')
    ws = [w for s in segs for w in (s.words or [])]
    hyp = cc.convert(''.join(w.word for w in ws))
    r = ''.join(_norm(c['text'], cc)); h = ''.join(_norm(hyp, cc))
    sm = difflib.SequenceMatcher(None, r, h, autojunk=False)
    rec = sum(b.size for b in sm.get_matching_blocks()) / max(1, len(r))   # how much of the cue text is heard in its window
    st = round(float(ws[0].start) - (c['t0'] - s0), 2) if ws else None
    res.append(dict(t0=c['t0'], t1=c['t1'], text=c['text'], heard=hyp, recall=round(rec, 2), sim=round(sm.ratio(), 2), start_offset=st))
rc = [x['recall'] for x in res]; sims = [x['sim'] for x in res]
off = [x for x in res if x['start_offset'] is not None and abs(x['start_offset']) >= 0.9]
a1 = ''.join(''.join(_norm(c['text'], cc)) for c in fine); b1 = ''.join(''.join(_norm(l['text'], cc)) for l in S)
summ = dict(duration=round(dur, 1), cues=len(fine), over18=sum(len(c['text']) > 18 for c in fine), max_chars=max(len(c['text']) for c in fine),
            text_complete=a1 == b1, recall_mean=round(sum(rc) / len(rc), 3), sim_mean=round(sum(sims) / len(sims), 3),
            low_recall_lt_0_6=sum(r < 0.6 for r in rc), offset_ge_0_9s=len(off))
json.dump(dict(summary=summ, cues=res), open(outp, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(json.dumps(summ, ensure_ascii=False))
for x in res:
    if x['recall'] < 0.6: print('LOW', x['t0'], x['text'], '|', x['heard'], x['recall'])

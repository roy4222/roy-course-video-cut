"""youtube.json + thumb for an out/SECxx dir (qc/ holds cues.json script.json scenes.json meta.json). usage: r2_pack.py <outdir> <NN>"""
import sys, json, re, os, subprocess
O, NN = sys.argv[1], sys.argv[2]; q = lambda f: json.load(open(os.path.join(O, 'qc', f), encoding='utf-8'))
meta, S, cues, sc = q('meta.json'), q('script.json'), q('cues.json'), {s['id']: s for s in q('scenes.json')}
orig = json.load(open(os.path.join(os.environ['SEC_SERIES'], f'ep{NN}', 'meta.json'), encoding='utf-8'))
if orig.get('summary'): meta['summary'] = orig['summary']
fmt = lambda s: f'{int(s)//60}:{int(s)%60:02d}'
first, order = {}, []
for l, c in zip(S, cues):
    if l['sc'] not in first: first[l['sc']] = c['t0']; order.append(l['sc'])
ch = '\n'.join(f"{fmt(0 if i == 0 else first[s] - 0.9)} {sc[s].get('title') or sc[s].get('chapter') or meta['title']}" for i, s in enumerate(order))
bad = re.compile(r'[A-Za-z]:\\|/home/\S*|/Users/\S*|/workspace\S*|localhost\S*|127\.0\.0\.1\S*|sk-or-\S*')
src = [bad.sub('', s).strip(' ：:；;，,') for s in meta.get('sources', [])]
src = [s for s in src if s]
desc = meta['summary'] + '\n\n章節\n' + ch + ('\n\n參考課程與資料\n' + '\n'.join(src) if src else '') + '\n\n' + meta.get('about', '')
y = dict(title=f"{meta.get('series','系統與軟體安全')} EP{NN}｜{meta['title']}", description=desc, tags=meta.get('tags', []), synthetic=True,
         language='zh-TW', category='Education', video_file=f'SEC{NN}.mp4', captions_file=f'SEC{NN}.srt')
s = json.dumps(y, ensure_ascii=False)
assert not bad.search(s), 'leak'
json.dump(y, open(os.path.join(O, 'youtube.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', '4', '-i', os.path.join(O, f'SEC{NN}.mp4'), '-frames:v', '1', '-vf', 'scale=1280:-2', '-q:v', '3', os.path.join(O, 'thumb.jpg')], check=True)
print('chapters:', len(order), 'sources:', len(src), 'desc chars', len(desc))

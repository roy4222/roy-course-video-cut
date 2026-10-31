import json, re, sys
from pathlib import Path
def esc(s): return s.replace('\\','\\\\').replace("'","\\'")
def convert(ep_dir):
    ep_dir=Path(ep_dir)
    meta=json.loads((ep_dir/'meta.json').read_text(encoding='utf-8'))
    md=(ep_dir/'script.md').read_text(encoding='utf-8')
    SER='系統與軟體安全'
    ABOUT=('「系統與軟體安全」從零基礎鉤子開始，銜接到 Berkeley CS161、Stanford CS155、MIT 6.566，'
           '並穿插真實事故、Bug Bounty 與逆向工具。旁白為 AI 合成語音；畫面含程式圖解與真實公開來源查證。數字與連結於 2026-10-31 查證。')
    sources=[s if len(s)<200 else s[:197]+'…' for s in meta.get('sources',[])]
    scenes=[]
    for p in re.split(r'^##\s+',md,flags=re.M)[1:]:
        lines=p.splitlines(); m=re.match(r'(\d+[a-z]?)\.\s*(.+)',lines[0].strip())
        sc=dict(num=m.group(1) if m else f'x{len(scenes)}',title=m.group(2) if m else lines[0].strip(),
                style='whiteboard',desc='',assets=[],recording=None,cite=None,narr=[])
        for l in lines[1:]:
            v=l.split('：',1)[-1].strip()
            if l.startswith('**style**'): sc['style']=v
            elif l.startswith('**畫面**'): sc['desc']=v
            elif l.startswith('**assets**') and v and v!='—': sc['assets']=[a.strip() for a in v.split(',')]
            elif l.startswith('**recording**'): sc['recording']=v
            elif l.startswith('**來源角標**'): sc['cite']=v
            elif l.startswith('- '): sc['narr'].append(l[2:].strip())
        scenes.append(sc)
    n=meta['num']; short=meta.get('short') or f'SEC{n:02d}'
    o=[f"# SEC{n:02d} {meta['title']}","from lib import Ep",f"SER='{SER}'",f"ABOUT='{esc(ABOUT)}'","SOURCES=["]
    o+=[f"  '{esc(s)}'," for s in sources]+["]"]
    tags="["+", ".join("'"+esc(t)+"'" for t in meta.get('tags',[SER])[:10])+"]"
    o+=[f"ep=Ep({n}, '{esc(meta['title'])}', '{esc(short)}', '{esc((meta.get('summary') or '')[:220])}', {tags}, '{esc(meta.get('next') or '')}',",
        "   accent='A', series=SER, about=ABOUT, ref_label='來源', sources=SOURCES)","E, L = ep.E, ep.L",""]
    ACC={'caption-news':'BAD','visual-investigation':'BAD','teardown':'BAD','iso-infographic':'PUR'}
    for i,sc in enumerate(scenes):
        sid='s'+sc['num']; ch=esc(sc['title'][:12]); acc=ACC.get(sc['style'],'A')
        if i==0 and sc['style']=='titlecard':
            o.append(f"ep.scene('{sid}', '', noHeader=True, chapter='{ch}', desc='{esc(sc['desc'][:40])}')")
            o.append(f"E('titlecard', ep='SEC{n:02d}', title='{esc(meta['title'][:18])}', sub='{esc(short)}', size=72)")
        else:
            ref=f", ref='{esc(sc['cite'][:80])}'" if sc['cite'] else ''
            o.append(f"ep.scene('{sid}', '{esc(sc['title'][:28])}', chapter='{ch}', desc='{esc(sc['desc'][:50])}'{ref})")
        for j,l in enumerate(sc['narr']):
            o.append((f"a{j} = ")+f"L('{esc(l)}')")
        if not sc['narr']: o.append("a0 = L('…')")
        N=max(1,len(sc['narr'])); o.append("c = a0")
        at=", at=a0"; st=sc['style']
        if i==0 and st=='titlecard': pass
        elif st=='iso-infographic':
            o.append("E('chips', y=280, items=["+", ".join(f"dict(s='{esc(x[:16])}', at=a{min(k,N-1)})" for k,x in enumerate(sc['narr'][:4]))+"], size=26)")
        elif st=='whiteboard':
            b=(sc['narr'][1:5] if len(sc['narr'])>2 else sc['narr'][:3]) or [sc['title']]
            o.append("E('bullets', x=160, y=240, items=["+", ".join(f"'{esc(x[:36])}'" for x in b)+f"], size=28{at})")
        elif st=='blueprint':
            o.append("E('flow', x=150, y=260, w=1620, h=140, gap=36, size=24, subSize=18, items=["+", ".join(f"dict(s='{esc(x[:10])}', sub='', col='A', at=a{min(k,N-1)})" for k,x in enumerate(sc['narr'][:4]))+"])")
        else:
            body=[sc['recording'] or ''] if st=='living-screencast' else sc['narr'][:2]
            body=[x for x in body if x] or [sc['desc'][:40] or sc['title']]
            title='實機畫面' if st=='living-screencast' else sc['title'][:24]
            o.append(f"E('card', x=120, y=200, w=1680, h=220, title='{esc(title)}', ts=28, col='{acc}', body=["+", ".join(f"'{esc(x[:40])}'" for x in body)+f"], bs=26{at})")
        if sc['cite'] and st not in ('titlecard',):
            o.append(f"E('cite', items=['{esc(sc['cite'][:60])}'], y=840{at})")
        o.append("")
    o.append("ep.save('.')")
    (ep_dir/'build.py').write_text('\n'.join(o)+'\n',encoding='utf-8')
    compile('\n'.join(o),'build.py','exec')
    ch=sum(len(l) for s in scenes for l in s['narr'])
    print(ep_dir.name,'scenes',len(scenes),'chars',ch,'est_min',round(ch/220,1))
for d in sys.argv[1:]: convert(d)

import os
"""script.md+meta.json -> build.py using screenshots (img) and recording frames; plus media bundle film_media/."""
import json, re, sys, subprocess, shutil
from pathlib import Path
def esc(s): return str(s).replace('\\','\\\\').replace("'","\\'").replace('\n',' ')
def credit(p):
    c=p.with_suffix('.credit.txt')
    if not c.exists(): c=Path(str(p).rsplit('.',1)[0]+'.credit.txt')
    if c.exists():
        t=c.read_text(encoding='utf-8').strip().splitlines()[0]
        t=re.sub(r'https?://(www\.)?','',t)
        return t[:90]
    return ''
def frames(mp4, outdir, fps=5):
    outdir.mkdir(parents=True, exist_ok=True)
    if not any(outdir.glob('*.jpg')):
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp4),'-vf',f'fps={fps},scale=1600:-2','-q:v','4',str(outdir/'%04d.jpg')],check=True)
    return len(list(outdir.glob('*.jpg')))
def convert(ep_dir):
    ep=Path(ep_dir); meta=json.loads((ep/'meta.json').read_text(encoding='utf-8')); md=(ep/'script.md').read_text(encoding='utf-8')
    media=ep/'film_media'; 
    if media.exists(): shutil.rmtree(media)
    (media/'img').mkdir(parents=True)
    SER='系統與軟體安全'
    ABOUT=('「系統與軟體安全」從零基礎鉤子開始，銜接到 Berkeley CS161、Stanford CS155、MIT 6.566，'
           '並穿插真實事故、Bug Bounty 與逆向工具。旁白為 AI 合成語音；畫面含真實工具錄屏、公開網頁截圖（角標出處）與圖解。數字與連結於 2026-10-31 查證。')
    scenes=[]
    for p in re.split(r'^##\s+',md,flags=re.M)[1:]:
        lines=p.splitlines(); m=re.match(r'(\d+[a-z]?)\.\s*(.+)',lines[0].strip())
        sc=dict(num=m.group(1) if m else f'x{len(scenes)}',title=m.group(2) if m else lines[0].strip(),style='whiteboard',desc='',assets=[],recs=[],cite=None,narr=[])
        for l in lines[1:]:
            v=l.split('：',1)[-1].strip()
            if l.startswith('**assets**') or l.startswith('**recording**'): v=re.sub(r'（[^）]*）|\([^)]*\)','',v).strip()
            if l.startswith('**style**'): sc['style']=v
            elif l.startswith('**畫面**'): sc['desc']=v
            elif l.startswith('**assets**') and v and v not in('—','-'): sc['assets']=[a.strip() for a in re.split(r'[,，、]',v) if a.strip()]
            elif l.startswith('**recording**') and v and v not in('—','-'): sc['recs']=[a.strip().split()[0] for a in re.split(r'[,，、]',v) if a.strip()]
            elif l.startswith('**來源角標**'): sc['cite']=v
            elif l.startswith('- '): sc['narr'].append(l[2:].strip())
        scenes.append(sc)
    import re as _re
    _nn=meta['num']; n=int(_re.search(r'\d+',str(_nn)).group()); LAB=(str(_nn) if str(_nn)[:1].isalpha() else f'SEC{_nn}') if isinstance(_nn,str) else f'SEC{n:02d}'; short=meta.get('short') or LAB
    o=[f"# {LAB} {meta['title']}","from lib import Ep",f"SER='{SER}'",f"ABOUT='{esc(ABOUT)}'","SOURCES=["]
    o+=[f"  '{esc(s)}'," for s in meta.get('sources',[])]+["]"]
    tags="["+", ".join("'"+esc(t)+"'" for t in meta.get('tags',[SER])[:12])+"]"
    o+=[f"ep=Ep({n}, '{esc(meta['title'])}', '{esc(short)}', '{esc((meta.get('summary') or '')[:240])}', {tags}, '{esc(meta.get('next') or '')}',",
        "   accent='A', series=SER, about=ABOUT, ref_label='來源', sources=SOURCES)","E, L = ep.E, ep.L",""]
    ACC={'caption-news':'BAD','visual-investigation':'BAD','teardown':'BAD','iso-infographic':'PUR'}
    nimg=nrec=0; missing=[]
    for i,sc in enumerate(scenes):
        sid='s'+sc['num']; ch=esc(sc['title'][:12]); acc=ACC.get(sc['style'],'A'); st=sc['style']
        if i==0 and st=='titlecard':
            o.append(f"ep.scene('{sid}', '', noHeader=True, chapter='{ch}', desc='{esc(sc['desc'][:40])}')")
        else:
            ref=f", ref='{esc(sc['cite'][:80])}'" if sc['cite'] else ''
            o.append(f"ep.scene('{sid}', '{esc(sc['title'][:30])}', chapter='{ch}', desc='{esc(sc['desc'][:50])}'{ref})")
        N=len(sc['narr']) or 1
        for j,l in enumerate(sc['narr']): o.append(f"a{j} = L('{esc(l)}')")
        if not sc['narr']: o.append("a0 = L('…')")
        # visuals: recordings first, then images
        vis=[]
        for r in sc['recs']:
            rp=ep/r
            if rp.suffix=='.mp4' and rp.exists():
                nm=rp.stem; cnt=frames(rp, media/'rec'/nm); vis.append(('rec',nm,cnt,credit(rp))); nrec+=1
            elif rp.suffix!='.cast': missing.append(r)
        for a in sc['assets']:
            ap=ep/a
            if ap.exists() and ap.suffix.lower() in('.png','.jpg','.jpeg','.webp'):
                shutil.copy(ap, media/'img'/ap.name); vis.append(('img',ap.name,0,credit(ap))); nimg+=1
            else: missing.append(a)
        if i==0 and st=='titlecard':
            o.append(f"E('titlecard', ep='{LAB}', title='{esc(meta['title'][:20])}', sub='{esc(short)}', size=70)")
            if vis:
                kind,nm,cnt,cr=vis[0]
                if kind=='img': o.append(f"E('img', src='img/{esc(nm)}', x=560, y=640, w=800, h=300, fit='cover', credit='{esc(cr)}', at=a{min(1,N-1)})")
        elif vis:
            k=len(vis); starts=[round(x*N/k) for x in range(k)]
            for vi,(kind,nm,cnt,cr) in enumerate(vis):
                s=min(starts[vi],N-1); u=f", until=a{starts[vi+1]}" if vi+1<k and starts[vi+1]<N else ''
                lab='實機錄屏' if kind=='rec' else ''
                if kind=='rec':
                    o.append(f"E('img', frames=dict(dir='rec/{esc(nm)}', n={cnt}, fps=5), x=160, y=180, w=1600, h=640, fit='contain', label='{lab}', credit='{esc(cr)}', at=a{s}{u})")
                else:
                    o.append(f"E('img', src='img/{esc(nm)}', x=160, y=180, w=1600, h=640, fit='cover', pan='down', col='{acc}', credit='{esc(cr)}', at=a{s}{u})")
        else:
            if st=='iso-infographic':
                o.append("E('chips', y=300, items=["+", ".join(f"dict(s='{esc(x[:16])}', at=a{min(kk*max(1,N//4),N-1)})" for kk,x in enumerate(sc['narr'][:4]))+"], size=28)")
            elif st=='blueprint':
                o.append("E('flow', x=150, y=300, w=1620, h=150, gap=36, size=24, subSize=18, items=["+", ".join(f"dict(s='{esc(x[:10])}', sub='', col='A', at=a{min(kk*max(1,N//4),N-1)})" for kk,x in enumerate(sc['narr'][:4]))+"])")
            else:
                pick=sc['narr'][:5] if N<=5 else [sc['narr'][round(x*(N-1)/4)] for x in range(5)]
                idx=[sc['narr'].index(x) for x in pick]
                o.append("E('bullets', x=160, y=210, w=1600, items=["+", ".join(f"dict(s='{esc(x[:38])}', at=a{ix})" for x,ix in zip(pick,idx))+"], size=28, col='"+acc+"')")
        if sc['cite'] and not (i==0 and st=='titlecard'):
            o.append(f"E('cite', items=['{esc(sc['cite'][:70])}'], y=878, at=a0)")
        o.append("")
    o.append("ep.save('.')")
    (ep/'build.py').write_text('\n'.join(o)+'\n',encoding='utf-8'); compile('\n'.join(o),'build.py','exec')
    ch=sum(len(l) for s in scenes for l in s['narr'])
    print(ep.name,'scenes',len(scenes),'chars',ch,'est',round(ch/220,1),'min imgs',nimg,'recs',nrec,'missing',missing)
import subprocess
for d in sys.argv[1:]:
    convert(d)
    if os.path.isdir(os.path.join(d,'film_media','rec')): subprocess.run(['python3',os.path.join(os.path.dirname(os.path.abspath(__file__)),'trim_dark_tail.py'),d,os.path.join(d,'film_media')])

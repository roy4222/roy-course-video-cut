# LEGACY pipeline B. New episodes use windows-kit/make_episode.py. Path defaults match the 2026-10-30 box; see legacy/README.md.
"""pipe.py <epdir> <step...>   steps: tts timeline layout render mix srt qc yt md all"""
import json,os,sys,subprocess,time,wave,re,difflib
VS=os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style');LIB=os.environ.get('LEMO_OPUSCAR',VS+'/lemo-opuscar');ENG=os.environ.get('EP_ENGINE',VS+'/epB_engine')
sys.path.insert(0,LIB+'/core/tts')
PY=os.environ.get('VIDEO_STYLE_PYTHON','/workspace/venv/bin/python')
D=os.path.abspath(sys.argv[1]);steps=sys.argv[2:]
if steps==['all']: steps=['tts','timeline','layout','render','mix','srt','md','qc','yt']
os.chdir(D);os.makedirs('voice',exist_ok=True);os.makedirs('qc',exist_ok=True);os.makedirs('out',exist_ok=True)
S=json.load(open('script.json'));meta=json.load(open('meta.json'));N=meta['num']
def log(*a):
    print(*a,flush=True);open('pipe.log','a').write(time.strftime('%H:%M:%S ')+' '.join(map(str,a))+'\n')
def progress(**kw):
    p=VS+'/progress_B.json';P=json.load(open(p)) if os.path.exists(p) else {}
    e=P.setdefault(f'EP{N:02d}',{});e.update(kw);e['updated']=time.strftime('%Y-%m-%d %H:%M')
    json.dump(P,open(p+'.tmp','w'),ensure_ascii=False,indent=1);os.replace(p+'.tmp',p)
say=lambda l:l.get('say') or l['text']
def chunks():
    out=[];order=[]
    for l in S:
        if l['sc'] not in order: order.append(l['sc'])
    for sc in order:
        L=[l for l in S if l['sc']==sc];cur=[];n=0;k=0
        for l in L:
            if cur and n+len(say(l))>380:
                out.append((f'{sc}__{k}',cur));k+=1;cur=[];n=0
            cur.append(l);n+=len(say(l))
        out.append((f'{sc}__{k}',cur))
    return out
def tts():
    import tts_openrouter as T
    sys.path.insert(0,ENG); from my_align import split_scene
    from faster_whisper import WhisperModel
    cp='voice/costs.json';costs=json.load(open(cp)) if os.path.exists(cp) else {}
    os.makedirs('voice/scenes',exist_ok=True);asr=None;match={}
    mp='voice/match.json';match=json.load(open(mp)) if os.path.exists(mp) else {}
    def synth(text,out,key):
        wait=60
        for r in range(8):
            try:
                g=T.synth(text,out,T.DEFAULT_MODEL,T.DEFAULT_VOICE,T.DEFAULT_INS,tries=12)
                c=T.cost(g) if g else None;costs[key]=c;json.dump(costs,open(cp,'w'),indent=0);return c
            except Exception as e:
                log('  synth retry',key,str(e)[:100],'sleep',wait);time.sleep(wait);wait=min(wait*2,600)
        raise RuntimeError('tts failed '+key)
    for cid,L in chunks():
        outs=[f"voice/{l['id']}.wav" for l in L]
        if all(os.path.exists(o) for o in outs) and all(match.get(l['id'],1)>=0.5 for l in L): continue
        sw=f'voice/scenes/{cid}.wav'
        if os.path.exists(os.path.join(ENG,'linemode')):
            for l,o in zip(L,outs):
                if match.get(l['id'],0)<0.5 or not os.path.exists(o):
                    synth(say(l),o+'.tmp.wav','line:'+l['id']);T.trim(o+'.tmp.wav',o);os.remove(o+'.tmp.wav');match[l['id']]=1.0
                    json.dump(match,open(mp,'w'),indent=0)
            log(cid,'line mode done');continue
        for attempt in range(3):
            if not os.path.exists(sw):
                c=synth('\n'.join(say(l) for l in L),sw,'scene:'+cid+(f'#{attempt}' if attempt else ''));log(cid,len(L),'lines cost',c)
            asr=asr or WhisperModel('small',device='cpu',compute_type='int8')
            try:
                if len(L)==1:
                    T.trim(sw,outs[0]);r=[{'match':1.0}]
                else:
                    r,_=split_scene(asr,sw,[say(l) for l in L],outs)
                ms=[x['match'] for x in r];log(cid,'match',ms)
                for l,x in zip(L,r): match[l['id']]=x['match']
                json.dump(match,open(mp,'w'),indent=0)
                if min(ms)<0.5:
                    raise RuntimeError('low match %s'%ms)
                break
            except RuntimeError as e:
                log(cid,'align fail -> line mode',str(e)[:120])
                for l,o in zip(L,outs):
                    if match.get(l['id'],0)<0.5 or not os.path.exists(o):
                        synth(say(l),o+'.tmp.wav','line:'+l['id']);T.trim(o+'.tmp.wav',o);os.remove(o+'.tmp.wav');match[l['id']]=1.0
                        json.dump(match,open(mp,'w'),indent=0)
                break
    dur={l['id']:round(wave.open(f"voice/{l['id']}.wav").getnframes()/24000,3) for l in S}
    json.dump(dur,open('voice/dur.json','w'),indent=0)
    tot=sum(v or 0 for v in costs.values());log('TTS done speech %.1fs cost US$%.4f'%(sum(dur.values()),tot));progress(tts_cost=round(tot,4),tts='done')
def timeline():
    dur=json.load(open('voice/dur.json')) if os.path.exists('voice/dur.json') else {l['id']:len(say(l))/4.75 for l in S};t=1.2;prev=None;cues=[];L2=[]
    for l in S:
        if prev is not None and l['sc']!=prev: t+=1.2
        t0=round(t,3);t1=round(t0+dur[l['id']],3);L2.append(dict(id=l['id'],sc=l['sc'],text=l['text'],t0=t0,t1=t1));cues.append(dict(t0=t0,t1=t1,text=l['text']))
        t=t1+0.7+(l.get('gap') or 0);prev=l['sc']
    DUR=round(L2[-1]['t1']+2.5,2)
    os.makedirs('film',exist_ok=True)
    sc=json.load(open('scenes.json'))
    em=dict(head=f"EP{N:02d} · {meta['title']}",accent=meta.get('accent','A'))
    open('film/timeline.js','w').write('window.LINES='+json.dumps(L2,ensure_ascii=False)+';\nwindow.SCENES='+json.dumps(sc,ensure_ascii=False)+';\nwindow.EPMETA='+json.dumps(em,ensure_ascii=False)+f';\nwindow.DUR={DUR};\n')
    subprocess.run(['cp',ENG+'/engine.js','film/main.js'],check=True)
    open('film/index.html','w').write('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#0f1115;overflow:hidden}canvas{display:block}</style></head>\n<body><canvas id="c" width="1920" height="1080"></canvas><script src="timeline.js"></script><script src="main.js"></script></body></html>\n')
    json.dump(cues,open('cues.json','w'),ensure_ascii=False,indent=0)
    log('timeline DUR %.1fs (%.1f min)'%(DUR,DUR/60));progress(duration_s=DUR)
def layout():
    r=subprocess.run(['node',ENG+'/layout.mjs',D+'/film'],cwd=LIB,capture_output=True,text=True);open('qc/layout.txt','w').write(r.stdout+r.stderr);log('layout:',r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-300:])
def render():
    slots=os.environ.get('WK','3')
    r=subprocess.run(['node','core/render/video.mjs',D+'/film','--fps','30','--workers',slots,'--out',D+'/out/video.mp4'],cwd=LIB,capture_output=True,text=True)
    open('render.log','w').write(r.stdout[-3000:]+r.stderr[-3000:]);assert r.returncode==0,r.stderr[-500:];log('render ok')
def mix():
    import numpy as np,soundfile as sf
    L2=json.loads(open('film/timeline.js').read().split('window.LINES=')[1].split(';\nwindow.SCENES')[0]);DUR=float(open('film/timeline.js').read().split('window.DUR=')[1].split(';')[0])
    sr=24000;buf=np.zeros(int(DUR*sr)+sr,dtype=np.float32)
    for l in L2:
        a,_=sf.read(f"voice/{l['id']}.wav",dtype='float32');i=int(l['t0']*sr);buf[i:i+len(a)]+=a[:len(buf)-i]
    sf.write('out/mix.wav',buf[:int(DUR*sr)],sr)
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i','out/mix.wav','-af','alimiter=limit=0.5:attack=5:release=50:level=disabled','out/mix_lim.wav'],check=True)
    r=subprocess.run(['sh','core/render/mux.sh',D+'/out/video.mp4',D+'/out/mix_lim.wav',D+f'/ep{N:02d}.mp4','30','0'],cwd=LIB,capture_output=True,text=True)
    open('mux.log','w').write(r.stdout+r.stderr);assert r.returncode==0,r.stderr[-800:];log('mux',re.findall(r'I:\s+(\S+) LUFS',r.stdout+r.stderr),re.findall(r'Peak:\s+(\S+)',r.stdout+r.stderr))
def srt():
    subprocess.run([PY,LIB+'/core/render/srt.py','cues.json',f'ep{N:02d}.srt'],check=True)
def fmt(s): s=int(s);return f'{s//60}:{s%60:02d}' if s<3600 else f'{s//3600}:{s//60%60:02d}:{s%60:02d}'
def starts():
    L2=json.loads(open('film/timeline.js').read().split('window.LINES=')[1].split(';\nwindow.SCENES')[0])
    order=[];first={}
    for l in L2:
        if l['sc'] not in first: first[l['sc']]=l['t0'];order.append(l['sc'])
    return [(sc,0 if i==0 else first[sc]-0.9) for i,sc in enumerate(order)]
def md():
    sc=json.load(open('scenes.json'));cues=json.load(open('cues.json'));dur=json.loads(open('film/timeline.js').read().split('window.DUR=')[1].split(';')[0])
    out=[f"# EP{N:02d} {meta['title']} — 腳本\n",f"- 長度：{fmt(dur)}｜風格 A：暗色架構圖｜旁白：Gemini TTS（Enceladus，台灣華語老師語氣）｜字幕：燒錄繁中＋另附 ep{N:02d}.srt",
         "- 每集結構：hook → 今日地圖 → 直覺 → 名詞 → 例題 → 常見誤區 → 測驗 → 回顧與預告","- 括號 [mm:ss] 為該句在成片中的開始時間；「（停頓 n 秒）」為留給觀眾思考的空白。\n"]
    for i,s in enumerate(sc):
        out.append(f"## {i:02d}. {s['title'] or s['chapter']}\n");out.append(f"**畫面**：{s.get('desc') or '—'}  \n**講義**：{s.get('ref') or '—'}\n")
        for l,c in zip(S,cues):
            if l['sc']==s['id']:
                out.append(f"- [{fmt(c['t0'])}] {l['text']}"+(f"（停頓 {l['gap']:.0f} 秒）" if l.get('gap') else ''))
        out.append('')
    open('script.md','w').write('\n'.join(out))
def qc():
    import opencc;cc=opencc.OpenCC('s2t')
    from faster_whisper import WhisperModel
    dur=float(json.loads(open('film/timeline.js').read().split('window.DUR=')[1].split(';')[0]));cues=json.load(open('cues.json'))
    mp=f'ep{N:02d}.mp4'
    ts=[round(dur*f,1) for f in (0.03,0.15,0.28,0.4,0.52,0.64,0.77,0.9)]
    for i,t in enumerate(ts): subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',mp,'-frames:v','1','-q:v','3',f'qc/f{i}_{int(t)}.jpg'],check=True)
    m=WhisperModel('base',device='cpu',compute_type='int8',cpu_threads=2);res=[]
    for f in (0.2,0.5,0.8):
        c=min(cues,key=lambda c:abs(c['t0']-dur*f))
        subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(c['t0']-1.0),'-t',str(c['t1']-c['t0']+1.5),'-i',mp,'-ac','1','-ar','16000','qc/sync.wav'],check=True)
        segs,_=m.transcribe('qc/sync.wav',language='zh',word_timestamps=True,condition_on_previous_text=False,vad_filter=True)
        words=[w for s in segs for w in s.words];hyp=cc.convert(''.join(w.word for w in words))
        st=words[0].start-1.0 if words else None;en=words[-1].end-1.0-(c['t1']-c['t0']) if words else None
        sim=difflib.SequenceMatcher(None,re.sub(r'\W','',c['text']),re.sub(r'\W','',hyp)).ratio()
        import soundfile as _sf,numpy as _np
        _a,_sr=_sf.read('qc/sync.wav');_w=int(0.02*_sr);_e=_np.sqrt(_np.convolve(_a**2,_np.ones(_w)/_w,mode='same'));_on=_np.where(_e>0.02)[0];_on=_on[_on>int(0.45*_sr)]
        e_on=round(_on[0]/_sr-1.0,2) if len(_on) else None;e_off=round(_on[-1]/_sr-1.0-(c['t1']-c['t0']),2) if len(_on) else None
        # energy within window: speech should start ~0 (line onset) and end ~0 (gap after line)
        res.append(dict(t=c['t0'],text=c['text'],heard=hyp,sim=round(sim,2),start_offset=round(st,2) if st is not None else None,end_offset=round(en,2) if en is not None else None,energy_onset=e_on,energy_end=e_off))
    json.dump(res,open('qc/sync.json','w'),ensure_ascii=False,indent=1);log('sync',[(r['sim'],r['start_offset']) for r in res])
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate','-of','json',mp],capture_output=True,text=True);log('probe',r.stdout.replace('\n',' ')[:300])
def yt():
    sc={s['id']:s for s in json.load(open('scenes.json'))}
    ch='\n'.join(f"{fmt(t)} {sc[s]['chapter']}" for s,t in starts())
    desc=meta['summary']+'\n\n章節\n'+ch+'\n\n'+'「機器學習從零開始」是一套給完全新手的機器學習補習影片，內容依照大學「機器學習」課程講義整理，用白話、生活例子和手算例題，一步一步帶你看懂。\n旁白為 AI 合成語音，畫面為程式生成的圖解。'
    y=dict(title=f"機器學習從零開始 EP{N:02d}｜{meta['title']}",description=desc,tags=meta['tags'],synthetic='yes',language='zh-TW',category='Education')
    s=json.dumps(y,ensure_ascii=False)
    assert not re.search(r'/home|/workspace|box|localhost|\b[0-9a-zA-Z_-]{25,}\b',s),'leak'
    json.dump(y,open('youtube.json','w'),ensure_ascii=False,indent=1);log('youtube.json ok')
for st in steps:
    t0=time.time();globals()[st]();log(f'step {st} done in {time.time()-t0:.0f}s')
    progress(**{'last_step':st})

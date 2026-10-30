# LEGACY pipeline C. New episodes use windows-kit/make_episode.py. Path defaults match the 2026-10-30 box; see legacy/README.md.
"""Build one episode end-to-end:  /workspace/venv/bin/python make_ep.py 02 [--stage all|script|tts|timeline|render|mux|qc|yt]
Episode source: /workspace/video_style/epNN/src.py defining META (dict) and SCENES (list)."""
import json,os,sys,subprocess,re,shutil,importlib.util,difflib,time
ROOT=os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style'); LEMO=os.environ.get('LEMO_OPUSCAR',ROOT+'/lemo-opuscar'); PY=os.environ.get('VIDEO_STYLE_PYTHON','/workspace/venv/bin/python'); LPY=os.environ.get('LEMO_PYTHON',LEMO+'/.venv/bin/python')
PROG=ROOT+'/progress_C.json'
def prog(ep,stage,val=True):
    import fcntl; lk=open(PROG+'.lock','w'); fcntl.flock(lk,fcntl.LOCK_EX)
    P=json.load(open(PROG)) if os.path.exists(PROG) else {}
    P.setdefault(ep,{})[stage]=val; P[ep]['updated']=time.strftime('%Y-%m-%d %H:%M'); json.dump(P,open(PROG,'w'),ensure_ascii=False,indent=1)
def done(ep,stage):
    P=json.load(open(PROG)) if os.path.exists(PROG) else {}
    return P.get(ep,{}).get(stage)
def sh(cmd,**kw):
    print('+',cmd if isinstance(cmd,str) else ' '.join(cmd),flush=True); subprocess.run(cmd,shell=isinstance(cmd,str),check=True,**kw)
def load(ep):
    d=f'{ROOT}/ep{ep}'; spec=importlib.util.spec_from_file_location('src',d+'/src.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return d,m
def stage_script(ep):
    d,m=load(ep); S=[];scenes={}
    for sc in m.SCENES:
        scenes[sc['id']]={k:v for k,v in sc.items() if k not in('lines','id')}
        for ln in sc['lines']:
            if isinstance(ln,str): ln={'text':ln}
            S.append({'sc':sc['id'],'text':ln['text'],'say':ln.get('say'),'gap':ln.get('gap',0.0)})
    cnt={}
    for l in S: cnt[l['sc']]=cnt.get(l['sc'],0)+1; l['id']=f"{l['sc']}_{cnt[l['sc']]-1:02d}"
    json.dump(S,open(d+'/script.json','w'),ensure_ascii=False,indent=0)
    json.dump(scenes,open(d+'/scenes.json','w'),ensure_ascii=False)
    md=[f"# {m.META['ep']} {m.META['title']} — 腳本",'',f"- 系列：{m.META['series']}",f"- 講義範圍：{m.META.get('slides','')}",'- 旁白：Gemini 3.8 Flash TTS（Enceladus）；字幕燒錄＋.srt','']
    for n,sc in enumerate(m.SCENES):
        md+=[f"## {n:02d}. {sc.get('title') or m.META['title']}",'',f"**講義**：{sc.get('ref','—')}  ",f"**畫面**：{', '.join(v['k'] for v in sc.get('v',[]))}",'']
        md+=[f"- {l['text']}"+(f"（停頓 {l['gap']} 秒）" if l['gap'] else '') for l in S if l['sc']==sc['id']]; md.append('')
    open(d+'/script.md','w').write('\n'.join(md)); n=sum(len(l['text']) for l in S); print('lines',len(S),'chars',n); prog(ep,'script',{'lines':len(S),'chars':n})
def stage_tts(ep):
    d,_=load(ep); import hashlib,glob
    S=json.load(open(d+'/script.json')); vd=d+'/voice'; os.makedirs(vd+'/scenes',exist_ok=True); hp=vd+'/scene_hash.json'
    H=json.load(open(hp)) if os.path.exists(hp) else {}; NH={}
    for sc in dict.fromkeys(l['sc'] for l in S):
        NH[sc]=hashlib.md5('\n'.join((l.get('say') or l['text']) for l in S if l['sc']==sc).encode()).hexdigest()
        if H.get(sc)!=NH[sc] and os.path.exists(vd+'/scenes/'+sc+'.wav'):
            cp=vd+'/costs.json'; C=json.load(open(cp)) if os.path.exists(cp) else {}
            for kk in [x for x in C if x.startswith('scene:'+sc) or x.startswith(sc+'_')]: C[f'old{time.time():.0f}:'+kk]=C.pop(kk)
            json.dump(C,open(cp,'w'))
            for f in [vd+'/scenes/'+sc+'.wav']+glob.glob(vd+'/'+sc+'_[0-9][0-9].wav'):
                if os.path.exists(f): os.remove(f); print('stale',f)
    json.dump(NH,open(hp,'w'))
    sh([PY,ROOT+'/common_C/align_ep.py',d+'/script.json',d+'/voice'])
    costs=json.load(open(d+'/voice/costs.json')); prog(ep,'tts',{'cost':round(sum(v or 0 for v in costs.values()),4),'missing_cost':sum(1 for v in costs.values() if v is None)})
def stage_timeline(ep):
    d,m=load(ep); S=json.load(open(d+'/script.json')); D=json.load(open(d+'/voice/dur.json')) if not os.environ.get('FAKE') else {l['id']:round(len(l['text'])*0.27,2) for l in json.load(open(d+'/script.json'))}; scenes=json.load(open(d+'/scenes.json'))
    t=1.2;prev=None;L=[];cues=[]
    for l in S:
        if prev is not None and l['sc']!=prev: t+=1.2
        du=D[l['id']]; L.append({'id':l['id'],'sc':l['sc'],'text':l['text'],'t0':round(t,3),'t1':round(t+du,3)}); cues.append({'t0':round(t,3),'t1':round(t+du,3),'text':l['text']})
        t+=du+0.7+(l.get('gap') or 0); prev=l['sc']
    DUR=round(L[-1]['t1']+2.4,2); f=d+'/film'; os.makedirs(f,exist_ok=True)
    open(f+'/timeline.js','w').write('window.LINES='+json.dumps(L,ensure_ascii=False)+';window.DUR='+str(DUR)+';window.SCENES='+json.dumps(scenes,ensure_ascii=False)+';window.META='+json.dumps(m.META,ensure_ascii=False)+';')
    shutil.copy(ROOT+'/common/engine.js',f+'/engine.js')
    open(f+'/index.html','w').write('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#0f1115;overflow:hidden}canvas{display:block}</style></head>\n<body><canvas id="c" width="1920" height="1080"></canvas><script src="timeline.js"></script><script src="engine.js"></script></body></html>')
    json.dump(cues,open(d+'/cues.json','w'),ensure_ascii=False,indent=0)
    link=f'{LEMO}/films/ep{ep}'
    if not os.path.islink(link): os.symlink(f,link)
    if not os.environ.get('FAKE'): prog(ep,'timeline',{'dur':DUR})
    else: print('FAKE DUR',DUR)
def stage_stills(ep,times):
    d,_=load(ep)
    if not times:
        C=json.load(open(d+'/cues.json')); S=json.load(open(d+'/script.json')); last={}
        for l,c in zip(S,C): last[l['sc']]=c['t1']
        times=[round(v-0.2,1) for v in last.values()]
    sh(['node',LEMO+'/core/render/still.mjs',f'films/ep{ep}']+[str(x) for x in times],cwd=LEMO)
def stage_render(ep):
    d,_=load(ep); os.makedirs(d+'/out',exist_ok=True)
    sh(['node',LEMO+'/core/render/video.mjs',f'films/ep{ep}','--fps','30','--workers',os.environ.get('WORKERS','2'),'--out',d+'/out/video.mp4'],cwd=LEMO); prog(ep,'render',True)
def stage_mux(ep):
    d,_=load(ep); import numpy as np,soundfile as sf
    S=json.load(open(d+'/script.json')); C=json.load(open(d+'/cues.json')); DUR=json.load(open(PROG))[ep]['timeline']['dur']
    SR=24000; mix=np.zeros(int(DUR*SR)+SR,dtype='float32')
    for l,c in zip(S,C):
        a,sr=sf.read(f"{d}/voice/{l['id']}.wav",dtype='float32'); s=int(c['t0']*SR); mix[s:s+len(a)]+=a
    sf.write(d+'/out/mix.wav',mix[:int(DUR*SR)],SR)
    sh(['ffmpeg','-loglevel','error','-y','-i',d+'/out/mix.wav','-af','alimiter=limit=0.5:attack=5:release=50:level=disabled','-ar','24000',d+'/out/mix_lim.wav'])
    r=subprocess.run(['sh',LEMO+'/core/render/mux.sh',d+'/out/video.mp4',d+'/out/mix_lim.wav',f'{d}/ep{ep}.mp4','30','0'],cwd=LEMO,capture_output=True,text=True); log=r.stdout+r.stderr; open(d+'/out/mux.log','w').write(log)
    I=re.findall(r'I:\s+(-?[\d.]+) LUFS',log); P=re.findall(r'Peak:\s+(-?[\d.]+) dBFS',log)
    sh([LPY,LEMO+'/core/render/srt.py',d+'/cues.json',f'{d}/ep{ep}.srt'])
    dur=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'{d}/ep{ep}.mp4'],capture_output=True,text=True).stdout)
    prog(ep,'mux',{'lufs':I[-1] if I else None,'peak':P[-1] if P else None,'duration':round(dur,2),'warn':'missed the target' in log})
def stage_qc(ep):
    d,_=load(ep); C=json.load(open(d+'/cues.json')); S=json.load(open(d+'/script.json')); os.makedirs(d+'/qc',exist_ok=True)
    order=[];[order.append(l['sc']) for l in S if l['sc'] not in order]
    first={};last={}
    for l,c in zip(S,C): first.setdefault(l['sc'],c['t0']); last[l['sc']]=c['t1']
    pick=[order[round(i*(len(order)-1)/7)] for i in range(8)]
    times=[round(first[sc]+0.75*(last[sc]-first[sc]),1) for sc in pick]
    for i,t in enumerate(times): sh(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',f'{d}/ep{ep}.mp4','-frames:v','1','-vf','scale=960:-2',f'{d}/qc/f{i}.jpg'])
    for j in (0,4): sh(['ffmpeg','-loglevel','error','-y']+sum([['-i',f'{d}/qc/f{j+i}.jpg'] for i in range(4)],[])+['-filter_complex','[0][1]hstack[a];[2][3]hstack[b];[a][b]vstack',f'{d}/qc/sheet{j//4+1}.jpg'])
    from faster_whisper import WhisperModel; import opencc; cc=opencc.OpenCC('s2t'); m=WhisperModel('small',device='cpu',compute_type='float32',cpu_threads=2)
    res=[]
    for i in (len(C)//6,len(C)//2,len(C)*5//6):
        c=C[i]; sh(['ffmpeg','-loglevel','error','-y','-ss',str(max(0,c['t0']-0.3)),'-to',str(c['t1']+0.3),'-i',f'{d}/ep{ep}.mp4','-vn','-ac','1','-ar','16000',os.environ.get('PIPELINE_TMP_WAV_C','/tmp/seg_C.wav')])
        segs,_=m.transcribe(os.environ.get('PIPELINE_TMP_WAV_C','/tmp/seg_C.wav'),language='zh',initial_prompt='以下是繁體中文的句子。'); h=cc.convert(''.join(x.text for x in segs))
        n=lambda s:re.sub(r'[\W_]','',s.lower()); r=difflib.SequenceMatcher(None,n(c['text']),n(h)).ratio()
        res.append({'t0':c['t0'],'sub':c['text'],'heard':h,'ratio':round(r,2)})
    json.dump({'frames':times,'scenes':pick,'sync':res},open(d+'/qc/qc.json','w'),ensure_ascii=False,indent=1); print(json.dumps(res,ensure_ascii=False))
    prog(ep,'qc',{'sync_min':min(x['ratio'] for x in res)})
def stage_yt(ep):
    d,m=load(ep); C=json.load(open(d+'/cues.json')); S=json.load(open(d+'/script.json')); sc=json.load(open(d+'/scenes.json'))
    order=[];[order.append(l['sc']) for l in S if l['sc'] not in order]
    first={}
    for l,c in zip(S,C): first.setdefault(l['sc'],c['t0'])
    fmt=lambda x:f"{int(x//60)}:{int(x%60):02d}"
    ch=[];
    for i,s0 in enumerate(order):
        st=0 if i==0 else max(0,first[s0]-0.9); name=sc[s0].get('chapter') or sc[s0].get('title') or '開場'
        if i==0: name=sc[s0].get('chapter') or '開場'
        if ch and st-ch[-1][0]<10: continue
        ch.append((st,name))
    desc='\n'.join(m.META['summary'])+'\n\n章節\n'+'\n'.join(f'{fmt(a)} {b}' for a,b in ch)+'\n\n'+m.META.get('note','「機器學習從零開始」系列：為完全新手設計的機器學習補習影片，依大學「機器學習」課程講義逐集整理。旁白為 AI 合成語音，畫面為程式繪製的圖解動畫。')
    Y={'title':m.META['yt_title'],'description':desc,'tags':m.META['tags'],'synthetic':True,'language':'zh-TW','video_file':f'ep{ep}.mp4','captions_file':f'ep{ep}.srt'}
    json.dump(Y,open(d+'/youtube.json','w'),ensure_ascii=False,indent=1); prog(ep,'yt',True); print(desc)
STAGES=['script','tts','timeline','render','mux','qc','yt']
if __name__=='__main__':
    ep=sys.argv[1]; st=sys.argv[2] if len(sys.argv)>2 else 'all'
    if st=='stills': stage_stills(ep,[float(x) for x in sys.argv[3:]]); sys.exit()
    for s in (STAGES if st=='all' else [st]):
        if st=='all' and done(ep,s) and s!='script': print('skip',s); continue
        print('=== stage',s,time.strftime('%H:%M:%S'),flush=True); globals()['stage_'+s](ep)
    print('DONE',ep,st,time.strftime('%H:%M:%S'))

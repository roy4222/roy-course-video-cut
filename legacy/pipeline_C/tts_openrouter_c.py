"""OpenRouter TTS (default voice for this project: google/gemini-3.8-flash-tts, voice Enceladus).

    OPENROUTER_API_KEY=... python core/tts/tts_openrouter.py lines.json out_dir [--mode scene|line]
        [--model google/gemini-3.8-flash-tts] [--voice Enceladus] [--instructions "..."]

lines.json = [{"id":..., "text":..., "say":"(optional spoken form)", "sc":"(scene id, used by --mode scene)"}, ...]
Writes out_dir/<id>.wav (24 kHz mono), out_dir/dur.json, out_dir/costs.json - same contract as tts_zh.py,
so the timeline / mux / srt steps don't change.

--mode scene (default): one request per scene (lines joined by newlines). Fewer requests (the upstream
  rate-limits hard: expect HTTP 429 and long back-offs) and more natural prosody across sentences.
  The scene audio is split back into lines by aligning faster-whisper word timestamps to the script
  (needs faster-whisper + opencc-python-reimplemented; falls back to nothing - it raises if alignment fails).
--mode line: one request per line (simple, but many more requests).
Never prints the API key. Per-request cost is read from /api/v1/generation?id=<X-Generation-Id>.
"""
import argparse,json,os,re,subprocess,sys,time,urllib.request,urllib.error
DEFAULT_MODEL='google/gemini-3.8-flash-tts'
DEFAULT_VOICE='Enceladus'
DEFAULT_INS=("Speak in Mandarin Chinese with a Taiwan Mandarin accent (台灣國語口音), like a warm, clear, friendly "
             "teacher explaining to a complete beginner, at a moderate, unhurried pace.")
def synth(text,out_wav,model,voice,ins,tries=20):
    key=os.environ.get('OPENROUTER_API_KEY') or sys.exit('tts_openrouter.py: OPENROUTER_API_KEY is not set')
    body={'model':model,'input':text,'voice':voice,'response_format':'pcm'}
    if ins: body['instructions']=ins
    wait=5
    for k in range(tries):
        req=urllib.request.Request('https://openrouter.ai/api/v1/audio/speech',data=json.dumps(body).encode(),
            headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
        try:
            r=urllib.request.urlopen(req,timeout=300); data=r.read(); ct=r.headers.get('Content-Type','')
            m=re.search(r'rate=(\d+)',ct); sr=m.group(1) if m else '24000'
            if len(data)<2000: raise RuntimeError('short audio')
            open(out_wav+'.pcm','wb').write(data)
            subprocess.run(['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',sr,'-ac','1','-i',out_wav+'.pcm','-ar','24000',out_wav],check=True)
            os.remove(out_wav+'.pcm'); return r.headers.get('X-Generation-Id')
        except urllib.error.HTTPError as e:
            print(f'  HTTP {e.code} (try {k+1}/{tries})',file=sys.stderr)
            if e.code not in (429,500,502,503,504): raise
        except Exception as e: print('  error',str(e)[:120],file=sys.stderr)
        time.sleep(wait); wait=min(wait*2,90)
    raise RuntimeError('tts_openrouter.py: gave up after retries')
def cost(gid):
    key=os.environ['OPENROUTER_API_KEY']
    for _ in range(8):
        time.sleep(2)
        try:
            req=urllib.request.Request('https://openrouter.ai/api/v1/generation?id='+gid,headers={'Authorization':'Bearer '+key})
            return json.load(urllib.request.urlopen(req,timeout=30))['data'].get('total_cost')
        except Exception: pass
def trim(src,dst):
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',src,'-af','silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse','-ar','24000','-ac','1',dst],check=True)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('lines'); ap.add_argument('out')
    ap.add_argument('--mode',default='scene',choices=['scene','line']); ap.add_argument('--model',default=DEFAULT_MODEL)
    ap.add_argument('--voice',default=DEFAULT_VOICE); ap.add_argument('--instructions',default=DEFAULT_INS)
    ap.add_argument('--asr-model',default='small'); a=ap.parse_args()
    L=json.load(open(a.lines)); os.makedirs(a.out,exist_ok=True)
    cp=os.path.join(a.out,'costs.json'); costs=json.load(open(cp)) if os.path.exists(cp) else {}
    say=lambda l: l.get('say') or l['text']
    if a.mode=='line':
        for l in L:
            o=os.path.join(a.out,l['id']+'.wav')
            if os.path.exists(o): continue
            g=synth(say(l),o+'.tmp.wav',a.model,a.voice,a.instructions); trim(o+'.tmp.wav',o); os.remove(o+'.tmp.wav')
            costs[l['id']]=cost(g) if g else None; json.dump(costs,open(cp,'w')); print(l['id'],costs[l['id']],flush=True)
    else:
        sys.path.insert(0,os.environ.get('LEMO_OPUSCAR','/workspace/video_style/lemo-opuscar')+'/core/tts'); from or_align import split_scene
        from faster_whisper import WhisperModel
        order=[];[order.append(l.get('sc','all')) for l in L if l.get('sc','all') not in order]
        sd=os.path.join(a.out,'scenes'); os.makedirs(sd,exist_ok=True); asr=None
        import threading; ready={sc:threading.Event() for sc in order}; lock=threading.Lock(); errs=[]
        def prefetch():
            for sc in order:
                G=[l for l in L if l.get('sc','all')==sc]; sw=os.path.join(sd,sc+'.wav')
                try:
                    if not os.path.exists(sw):
                        g=synth('\n'.join(say(l) for l in G),sw+'.part.wav',a.model,a.voice,a.instructions); os.replace(sw+'.part.wav',sw)
                        c=cost(g) if g else None
                        with lock: costs['scene:'+sc]=c; json.dump(costs,open(cp,'w'))
                        print(sc,c,flush=True)
                except Exception as e: errs.append(e)
                ready[sc].set()
        if os.environ.get('SYNTH_ONLY'):
            prefetch(); print('synth-only done',errs or '',flush=True); return
        threading.Thread(target=prefetch,daemon=True).start()
        for sc in order:
            G=[l for l in L if l.get('sc','all')==sc]; sw=os.path.join(sd,sc+'.wav')
            ready[sc].wait()
            if errs: raise errs[0]
            if all(os.path.exists(os.path.join(a.out,l['id']+'.wav')) for l in G): continue
            asr=asr or WhisperModel(a.asr_model,device='cpu',compute_type='int8',cpu_threads=3)
            outs=[os.path.join(a.out,l['id']+'.wav') for l in G]
            for attempt in range(3):
                try:
                    r,_=split_scene(asr,sw,[say(l) for l in G],outs); bad=[x['match'] for x in r if x['match']<0.45]
                    if bad: raise RuntimeError('low line match %s'%[x['match'] for x in r])
                    print(sc,'line match',[x['match'] for x in r],flush=True); break
                except RuntimeError as e:
                    print(sc,'ALIGN FAIL',attempt,e,flush=True)
                    for o in outs:
                        if os.path.exists(o): os.remove(o)
                    if attempt==0:
                        os.replace(sw,sw[:-4]+'.bad.wav')
                        g=synth('\n'.join(say(l) for l in G),sw,a.model,a.voice,a.instructions)
                        c=cost(g) if g else None
                        with lock: costs['scene:'+sc+':retry']=c; json.dump(costs,open(cp,'w'))
                    else:
                        for l,o in zip(G,outs):
                            g=synth(say(l),o+'.tmp.wav',a.model,a.voice,a.instructions); trim(o+'.tmp.wav',o); os.remove(o+'.tmp.wav')
                            c=cost(g) if g else None
                            with lock: costs[l['id']]=c; json.dump(costs,open(cp,'w'))
                        print(sc,'per-line fallback done',flush=True); break
    import wave
    dur={l['id']:round(wave.open(os.path.join(a.out,l['id']+'.wav')).getnframes()/24000,3) for l in L}
    json.dump(dur,open(os.path.join(a.out,'dur.json'),'w'),indent=0)
    print('total speech %.1fs  cost US$%.4f'%(sum(dur.values()),sum(v or 0 for v in costs.values())))
if __name__=='__main__': main()

import json,os,sys,time,urllib.request,urllib.error,subprocess
KEY=os.environ['OPENROUTER_API_KEY']
INS="Speak in Mandarin Chinese with a Taiwan Mandarin accent (台灣國語口音), like a warm, clear, friendly teacher explaining to a complete beginner, at a moderate, unhurried pace."
def synth(text,out_wav,voice='Enceladus',ins=INS,tries=8):
    body={'model':'google/gemini-3.8-flash-tts','input':text,'voice':voice,'response_format':'pcm'}
    if ins: body['instructions']=ins
    wait=5
    for k in range(tries):
        req=urllib.request.Request('https://openrouter.ai/api/v1/audio/speech',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
        try:
            r=urllib.request.urlopen(req,timeout=180); data=r.read(); h=dict(r.headers)
            ct=h.get('Content-Type',''); import re; m=re.search(r'rate=(\d+)',ct); sr=m.group(1) if m else '24000'
            if len(data)<2000: raise RuntimeError('short audio %d'%len(data))
            open(out_wav+'.pcm','wb').write(data)
            subprocess.run(['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',sr,'-ac','1','-i',out_wav+'.pcm','-ar','24000',out_wav],check=True); os.remove(out_wav+'.pcm')
            return h.get('X-Generation-Id') or h.get('x-generation-id')
        except urllib.error.HTTPError as e:
            msg=e.read()[:200].decode('utf8','replace'); ra=e.headers.get('Retry-After')
            print(f'  HTTP {e.code} try{k} {msg} retry-after={ra}',file=sys.stderr)
            if e.code not in (429,500,502,503,504): raise
            time.sleep(float(ra) if ra else wait); wait=min(wait*2,90)
        except Exception as e:
            print('  err',str(e)[:120],file=sys.stderr); time.sleep(wait); wait=min(wait*2,90)
    raise RuntimeError('gave up')
def cost(gid):
    for i in range(8):
        time.sleep(2)
        try:
            req=urllib.request.Request('https://openrouter.ai/api/v1/generation?id='+gid,headers={'Authorization':'Bearer '+KEY})
            return json.load(urllib.request.urlopen(req,timeout=30))['data'].get('total_cost')
        except Exception: pass
if __name__=='__main__':
    t=open('passage.txt').read().strip()
    g=synth(t,'enceladus_test.wav'); print('gid ok', cost(g))

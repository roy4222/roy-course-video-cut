import json,os,sys,subprocess,urllib.request,urllib.error,time
KEY=os.environ['OPENROUTER_API_KEY']
TEXT=open('passage.txt').read().strip()
INS="Speak in Mandarin Chinese with a Taiwan Mandarin accent (台灣國語口音), like a warm, clear, friendly teacher explaining to a beginner, at a moderate, unhurried pace."
def call(model,voice,ins=True,fmt='mp3',extra=None):
    body={'model':model,'input':TEXT,'response_format':fmt}
    if voice: body['voice']=voice
    if ins: body['instructions']=INS
    if extra: body.update(extra)
    req=urllib.request.Request('https://openrouter.ai/api/v1/audio/speech',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json'})
    try:
        r=urllib.request.urlopen(req,timeout=180); data=r.read(); return r.status,dict(r.headers),data
    except urllib.error.HTTPError as e:
        return e.code,dict(e.headers),e.read()
def cost(gid):
    for i in range(6):
        time.sleep(3)
        try:
            req=urllib.request.Request('https://openrouter.ai/api/v1/generation?id='+gid,headers={'Authorization':'Bearer '+KEY})
            j=json.load(urllib.request.urlopen(req,timeout=30))['data']
            return j.get('total_cost'),j.get('provider_name')
        except Exception as e: err=str(e)[:80]
    return None,err
jobs=json.loads(sys.argv[1])
res=json.load(open('results.json')) if os.path.exists('results.json') else {}
for model,voice,ins,fmt,extra in jobs:
    name=f"{model.split('/')[1]}_{(voice or 'default').split(':')[0].replace(' ','').replace('(','').replace(')','')}"
    st,h,data=call(model,voice,ins,fmt,extra)
    if st==400 and ins:
        st2,h2,d2=call(model,voice,False,fmt,extra)
        if st2==200: st,h,data,ins=st2,h2,d2,False
    ct=h.get('Content-Type') or h.get('content-type')
    rec={'model':model,'voice':voice,'instructions':ins,'status':st,'ctype':ct}
    if st==200 and not (ct or '').startswith('application/json'):
        raw=f'{name}.raw'; open(raw,'wb').write(data)
        if 'pcm' in (ct or '') or fmt=='pcm':
            sr='24000'
            import re; m=re.search(r'rate=(\d+)',ct or '');  sr=m.group(1) if m else sr
            cmd=['ffmpeg','-loglevel','error','-y','-f','s16le','-ar',sr,'-ac','1','-i',raw,'-b:a','128k',f'{name}.mp3']
        else:
            cmd=['ffmpeg','-loglevel','error','-y','-i',raw,'-ar','24000','-ac','1','-b:a','128k',f'{name}.mp3']
        subprocess.run(cmd,check=True); os.remove(raw)
        gid=h.get('X-Generation-Id') or h.get('x-generation-id'); rec['gen_id']=gid
        if gid: rec['cost'],rec['provider']=cost(gid)
        rec['file']=f'{name}.mp3'
    else:
        rec['error']=data[:400].decode('utf8','replace')
    res[name]=rec; print(name,json.dumps({k:v for k,v in rec.items() if k!='gen_id'},ensure_ascii=False)); sys.stdout.flush()
    json.dump(res,open('results.json','w'),ensure_ascii=False,indent=1)

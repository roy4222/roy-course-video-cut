"""prefetch.py <epdir>...: synthesize scene-chunk wavs ahead of alignment (same chunking as pipe.py). Costs -> voice/costs_pre.json"""
import json,os,sys,time
sys.path.insert(0,os.environ.get('LEMO_OPUSCAR','/workspace/video_style/lemo-opuscar')+'/core/tts')
import tts_openrouter as T
say=lambda l:l.get('say') or l['text']
def chunks(S):
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
for D in sys.argv[1:]:
    S=json.load(open(D+'/script.json'));os.makedirs(D+'/voice/scenes',exist_ok=True)
    cp=D+'/voice/costs_pre.json'
    for cid,L in chunks(S):
        sw=f'{D}/voice/scenes/{cid}.wav'
        if os.path.exists(sw) or all(os.path.exists(f"{D}/voice/{l['id']}.wav") for l in L): continue
        wait=30
        for r in range(10):
            try:
                g=T.synth('\n'.join(say(l) for l in L),sw+'.part.wav',T.DEFAULT_MODEL,T.DEFAULT_VOICE,T.DEFAULT_INS,tries=12);break
            except Exception as e:
                print('retry',cid,str(e)[:80],'sleep',wait,flush=True);time.sleep(wait);wait=min(wait*2,600)
        c=T.cost(g) if g else None
        costs=json.load(open(cp)) if os.path.exists(cp) else {};costs['scene:'+cid]=c;json.dump(costs,open(cp,'w'),indent=0)
        os.replace(sw+'.part.wav',sw);print(D[-4:],cid,c,flush=True)
print('prefetch done',flush=True)

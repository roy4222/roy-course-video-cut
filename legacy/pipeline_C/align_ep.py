"""usage: align_ep.py script.json voice_dir  -- synth missing scene audio (Gemini, Enceladus) and split with energy_align."""
import json,os,sys,wave
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from energy_align import split
import tts_openrouter_c as T
L=json.load(open(sys.argv[1])); out=sys.argv[2]; sd=out+'/scenes'; os.makedirs(sd,exist_ok=True)
cp=out+'/costs.json'; costs=json.load(open(cp)) if os.path.exists(cp) else {}
say=lambda l:l.get('say') or l['text']
order=list(dict.fromkeys(l['sc'] for l in L)); AL=json.load(open(out+'/align.json')) if os.path.exists(out+'/align.json') else {}
for sc in order:
    G=[l for l in L if l['sc']==sc]; outs=[f"{out}/{l['id']}.wav" for l in G]; sw=f'{sd}/{sc}.wav'
    if all(os.path.exists(o) for o in outs): continue
    if not os.path.exists(sw):
        g=T.synth('\n'.join(say(l) for l in G),sw+'.part.wav',T.DEFAULT_MODEL,T.DEFAULT_VOICE,T.DEFAULT_INS); os.replace(sw+'.part.wav',sw)
        costs['scene:'+sc]=T.cost(g) if g else None; json.dump(costs,open(cp,'w')); print(sc,'synth',costs['scene:'+sc],flush=True)
    try:
        r,ratio,pl=split(sw,[say(l) for l in G],outs); W=[len(say(l)) for l in G]; bad=[x for x,w in zip(ratio,W) if ((x<0.6 or x>1.6) if w>=20 else (x<0.4 or x>2.2))]
    except RuntimeError as e: bad=[str(e)]; ratio=pl=[]
    if bad:
        print(sc,'SPLIT SUSPECT',ratio,pl,'-> per-line synth',flush=True)
        for l,o in zip(G,outs):
            g=T.synth(say(l),o+'.tmp.wav',T.DEFAULT_MODEL,T.DEFAULT_VOICE,T.DEFAULT_INS); T.trim(o+'.tmp.wav',o); os.remove(o+'.tmp.wav')
            costs[l['id']]=T.cost(g) if g else None; json.dump(costs,open(cp,'w'))
        AL[sc]={'mode':'per-line'}
    else:
        AL[sc]={'mode':'energy','ratio':[float(x) for x in ratio],'pauses':pl}; print(sc,'split',[float(x) for x in ratio],pl,flush=True)
    json.dump(AL,open(out+'/align.json','w'),ensure_ascii=False)
dur={l['id']:round(wave.open(f"{out}/{l['id']}.wav").getnframes()/24000,3) for l in L}
json.dump(dur,open(out+'/dur.json','w'),indent=0)
print('total speech %.1fs  cost US$%.4f'%(sum(dur.values()),sum(v or 0 for v in costs.values())))

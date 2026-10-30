import json,sys,os,time
_vt=os.environ.get('VOICE_TEST')
if not _vt:
    _c=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','legacy','tools','voice_test'))
    _vt=_c if os.path.isdir(_c) else '/workspace/video_style/voice_test'
sys.path.insert(0,_vt); import gem
S=json.load(open('script.json'))
order=[];[order.append(l['sc']) for l in S if l['sc'] not in order]
costs=json.load(open('voice_enc/scenes/costs.json')) if os.path.exists('voice_enc/scenes/costs.json') else {}
for sc in order:
    out=f'voice_enc/scenes/{sc}.wav'
    if os.path.exists(out): continue
    text='\n'.join((l.get('say') or l['text']) for l in S if l['sc']==sc)
    g=gem.synth(text,out,tries=20)
    costs[sc]=gem.cost(g) if g else None
    json.dump(costs,open('voice_enc/scenes/costs.json','w'))
    print(sc,len(text),costs[sc],flush=True); time.sleep(8)
print('cost total',sum(v or 0 for v in costs.values()))

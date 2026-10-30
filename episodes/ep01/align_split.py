"""Split per-scene TTS audio into per-line clips by aligning faster-whisper word timestamps to the script text."""
import json,sys,os,re,difflib
import numpy as np,soundfile as sf
from faster_whisper import WhisperModel
import opencc
cc=opencc.OpenCC('s2t')
def norm(s): return [c for c in cc.convert(s).lower() if re.match(r'[\w]',c) and c!='_']
def split_scene(model,wav,texts,outs,pad=0.06):
    a,sr=sf.read(wav,dtype='float32')
    segs,_=model.transcribe(wav,language='zh',vad_filter=False,word_timestamps=True,initial_prompt='以下是繁體中文的句子。')
    hyp=[];ht=[]
    for s in segs:
        for w in s.words:
            cs=norm(w.word)
            for k,c in enumerate(cs):
                hyp.append(c); ht.append(w.start+(w.end-w.start)*(k+0.5)/len(cs))
    ref=[];owner=[]
    for i,t in enumerate(texts):
        cs=norm(t); ref+=cs; owner+=[i]*len(cs)
    sm=difflib.SequenceMatcher(None,ref,hyp,autojunk=False)
    rt=[None]*len(ref)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): rt[blk.a+k]=ht[blk.b+k]
    n=len(texts); first=[None]*n; last=[None]*n; matched=[0]*n; tot=[0]*n
    for j,(o,t) in enumerate(zip(owner,rt)):
        tot[o]+=1
        if t is not None:
            matched[o]+=1
            if first[o] is None: first[o]=t
            last[o]=t
    # boundaries: quietest 30ms window between last[i] and first[i+1]
    win=int(0.03*sr); env=np.convolve(a**2,np.ones(win)/win,mode='same')
    cuts=[0]
    for i in range(n-1):
        lo=last[i] if last[i] is not None else None; hi=first[i+1] if first[i+1] is not None else None
        if lo is None or hi is None or hi<=lo:
            raise RuntimeError(f'alignment failed between line {i} and {i+1}: {lo} {hi}')
        s0,s1=int(lo*sr),int(hi*sr)
        cuts.append(s0+int(np.argmin(env[s0:s1])))
    cuts.append(len(a))
    thr=10**(-45/10)*1.0
    res=[]
    for i in range(n):
        seg=a[cuts[i]:cuts[i+1]]
        loud=np.where(env[cuts[i]:cuts[i+1]]>thr)[0]
        if len(loud): seg=seg[max(0,loud[0]-int(pad*sr)):min(len(seg),loud[-1]+int(pad*2*sr))]
        sf.write(outs[i],seg,sr); res.append({'dur':round(len(seg)/sr,3),'match':round(matched[i]/max(1,tot[i]),2)})
    return res,''.join(cc.convert(w) for w in hyp)
if __name__=='__main__':
    S=json.load(open('script.json'))
    m=WhisperModel('small',device='cpu',compute_type='int8')
    order=[];[order.append(l['sc']) for l in S if l['sc'] not in order]
    dur={};rep={}
    for sc in order:
        L=[l for l in S if l['sc']==sc]
        r,h=split_scene(m,f'voice_enc/scenes/{sc}.wav',[l.get('say') or l['text'] for l in L],[f"voice_enc/{l['id']}.wav" for l in L])
        for l,x in zip(L,r): dur[l['id']]=x['dur']; rep[l['id']]=x['match']
        print(sc,[x['match'] for x in r],flush=True)
    json.dump(dur,open('voice_enc/dur.json','w'),indent=0); json.dump(rep,open('voice_enc/match.json','w'),indent=0)
    print('total',sum(dur.values()))

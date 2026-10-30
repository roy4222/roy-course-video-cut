"""Fast ASR-free split of a per-scene TTS wav into per-line clips.
Finds pauses (low-energy runs) and picks N-1 of them with a DP that keeps each cut close to the
char-proportional expected position and prefers long pauses."""
import re,numpy as np,soundfile as sf
def _w(t): return max(1,len(re.sub(r'[\s，。、：；！？「」（）,.!?:;()\-—…]','',t)))+0.35*len(re.findall(r'[，。、：；！？,.!?:;]',t))
def split_scene_silence(wav,texts,outs,pad=0.06,min_pause=0.12):
    a,sr=sf.read(wav,dtype='float32'); n=len(texts)
    hop=int(0.01*sr); fr=len(a)//hop
    e=np.array([np.sqrt(np.mean(a[i*hop:(i+1)*hop]**2)+1e-12) for i in range(fr)])
    db=20*np.log10(e+1e-9); ref=np.percentile(db,90); sil=db<ref-32
    runs=[];i=0
    while i<fr:
        if sil[i]:
            j=i
            while j<fr and sil[j]: j+=1
            runs.append((i,j)); i=j
        else: i+=1
    speech=np.where(~sil)[0]; s0,s1=speech[0],speech[-1]
    cands=[((i+j)/2,(j-i)*0.01) for i,j in runs if (j-i)*0.01>=min_pause and i>s0 and j<s1]
    if n==1: cuts=[]
    else:
        if len(cands)<n-1: raise RuntimeError(f'only {len(cands)} pauses for {n} lines')
        w=np.array([_w(t) for t in texts]); cum=np.cumsum(w)[:-1]/w.sum()
        exp=[s0+c*(s1-s0) for c in cum]; T=s1-s0
        m=len(cands); INF=1e18
        D=np.full((n-1,m),INF); B=np.zeros((n-1,m),int)
        def cost(k,c):
            pos,dur=cands[c]; d=(pos-exp[k])/(0.08*T+50)
            return d*d-1.5*np.log(dur/0.12+1e-9)
        for c in range(m): D[0,c]=cost(0,c)
        for k in range(1,n-1):
            best=INF;bi=-1
            for c in range(m):
                if c-1>=0 and D[k-1,c-1]<best: best=D[k-1,c-1];bi=c-1
                if bi>=0: D[k,c]=best+cost(k,c);B[k,c]=bi
        c=int(np.argmin(D[n-2])); sel=[c]
        for k in range(n-2,0,-1): c=B[k,c]; sel.append(c)
        sel=sel[::-1]; cuts=[int(cands[c][0]*hop) for c in sel]
    cuts=[0]+cuts+[len(a)]; res=[]
    win=int(0.03*sr); env=np.convolve(a**2,np.ones(win)/win,mode='same'); thr=10**(-45/10)
    for i in range(n):
        seg=a[cuts[i]:cuts[i+1]]; loud=np.where(env[cuts[i]:cuts[i+1]]>thr)[0]
        if len(loud): seg=seg[max(0,loud[0]-int(pad*sr)):min(len(seg),loud[-1]+int(pad*2*sr))]
        sf.write(outs[i],seg,sr); res.append({'dur':round(len(seg)/sr,3),'rate':round(len(seg)/sr/_w(texts[i]),3)})
    # sanity: seconds per weighted char should be similar across lines
    r=np.array([x['rate'] for x in res]); med=np.median(r)
    bad=[i for i,x in enumerate(r) if x<med*0.55 or x>med*1.8]
    return res,bad

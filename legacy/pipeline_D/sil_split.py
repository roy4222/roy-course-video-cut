"""Split one scene TTS wav into per-line clips without ASR: pick N-1 pauses by DP (segment length vs char-proportional
expectation, longer pauses preferred). Returns per-line info with a confidence flag."""
import re,numpy as np,soundfile as sf
def _w(t): return max(1,len(re.sub(r'[\s，。、；：！？「」（）,.!?;:()\-—…／]','',t)))+0.6*len(re.findall(r'[，。、；：！？,.!?;:]',t))
def silences(a,sr,thr_db=-45,min_len=0.15,merge=0.1):
    win=int(0.02*sr);e=np.convolve(a**2,np.ones(win)/win,'same');sil=10*np.log10(e+1e-12)<thr_db
    runs=[];i=0;n=len(sil)
    while i<n:
        if sil[i]:
            j=i
            while j<n and sil[j]: j+=1
            runs.append([i,j]);i=j
        else: i+=1
    m=[]
    for r in runs:
        if m and (r[0]-m[-1][1])/sr<merge: m[-1][1]=r[1]
        else: m.append(r)
    return [(s/sr,e/sr) for s,e in m if (e-s)/sr>=min_len],e
def split(wav,texts,outs,pad=0.06):
    a,sr=sf.read(wav,dtype='float32');dur=len(a)/sr;n=len(texts)
    S,env=silences(a,sr)
    S=[s for s in S if s[0]>0.3 and s[1]<dur-0.3]
    w=np.array([_w(t) for t in texts]);E=dur*w/w.sum()
    if n==1: cuts=[]
    else:
        K=len(S);INF=1e18
        mids=[(s+e)/2 for s,e in S];lens=[e-s for s,e in S]
        def seg_cost(i,t0,t1):
            d=t1-t0;e=E[i];return ((d-e)/(0.14*e+0.6))**2
        # dp[b][k]: best cost having placed boundary b (0-based) at silence k
        dp=np.full((n-1,K),INF);bk=np.zeros((n-1,K),int)
        for k in range(K): dp[0][k]=seg_cost(0,0,mids[k])-3.0*lens[k]
        for b in range(1,n-1):
            for k in range(K):
                best=INF;arg=-1
                for j in range(k):
                    c=dp[b-1][j]+seg_cost(b,mids[j],mids[k])
                    if c<best: best=c;arg=j
                if arg>=0: dp[b][k]=best-3.0*lens[k];bk[b][k]=arg
        tot=[dp[n-2][k]+seg_cost(n-1,mids[k],dur) for k in range(K)]
        k=int(np.argmin(tot));ch=[k]
        for b in range(n-2,0,-1): k=bk[b][k];ch.append(k)
        ch=ch[::-1];cuts=[mids[k] for k in ch]
    bounds=[0]+cuts+[dur];res=[];thr=10**(-45/10)
    for i in range(n):
        s0,s1=int(bounds[i]*sr),int(bounds[i+1]*sr);seg=a[s0:s1];loud=np.where(env[s0:s1]>thr)[0]
        if len(loud): seg=seg[max(0,loud[0]-int(pad*sr)):min(len(seg),loud[-1]+int(2*pad*sr))]
        sf.write(outs[i],seg,sr)
        ratio=(bounds[i+1]-bounds[i])/E[i];pl=min([S[ch[i-1]][1]-S[ch[i-1]][0]] if i>0 else [9])
        res.append(dict(dur=round(len(seg)/sr,3),ratio=round(ratio,2),pause=round(pl if i>0 else 0,2)))
    conf=all(0.55<r['ratio']<1.7 for r in res) and all(r['pause']>=0.35 for r in res[1:])
    for r in res: r['match']=1.0 if conf else 0.4
    return res,conf

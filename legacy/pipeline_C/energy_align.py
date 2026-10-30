"""CPU-light fallback aligner: split per-scene TTS audio into per-line clips at the pauses between lines.
Gemini reads newline-joined lines with clear pauses; we pick the N-1 pauses (DP, monotonic) that best combine
pause length and closeness to the boundary expected from each line's share of characters."""
import numpy as np, soundfile as sf, re, json, os, sys
def weight(t):
    w=0.0
    for ch in t:
        if re.match(r'[\u4e00-\u9fff]',ch): w+=1
        elif ch.isdigit(): w+=0.9
        elif ch.isalpha(): w+=0.38
        elif ch in '，、；：。？！,;:?!': w+=0.55
        elif ch in '（）()「」—…': w+=0.15
    return max(w,1)
def frames(a,sr):
    hop=int(0.01*sr); n=len(a)//hop
    e=np.sqrt(np.mean(a[:n*hop].reshape(n,hop)**2,axis=1))+1e-9; return 20*np.log10(e),hop
def pauses(db,thr,minlen=10):
    low=db<thr; out=[];i=0;n=len(db)
    while i<n:
        if low[i]:
            j=i
            while j<n and low[j]: j+=1
            if j-i>=minlen: out.append((i,j))
            i=j
        else: i+=1
    return out
def split(wav,texts,outs,pad=0.06):
    a,sr=sf.read(wav,dtype='float32'); db,hop=frames(a,sr); thr=np.percentile(db,95)-35
    loud=np.where(db>=thr)[0]; s0,s1=loud[0],loud[-1]+1
    W=np.array([weight(t) for t in texts]); cw=np.cumsum(W)/W.sum(); n=len(texts)
    exp=[s0+(s1-s0)*c for c in cw[:-1]]
    P=[(i,j) for i,j in pauses(db,thr) if i>s0 and j<s1]
    if n>1 and len(P)<n-1: raise RuntimeError('not enough pauses')
    # DP over pauses: choose n-1 in order
    m=len(P); NEG=-1e9
    sc=lambda p,k:(P[p][1]-P[p][0])/100.0-0.35*abs((P[p][0]+P[p][1])/2-exp[k])/100.0
    best=[[NEG]*m for _ in range(n-1)]; arg=[[-1]*m for _ in range(n-1)]
    for k in range(n-1):
        run=NEG;ra=-1
        for p in range(m):
            if k==0: best[k][p]=sc(p,k)
            else:
                if p-1>=0 and best[k-1][p-1]>run: run=best[k-1][p-1]; ra=p-1
                if ra>=0: best[k][p]=run+sc(p,k); arg[k][p]=ra
    cuts=[0]
    if n>1:
        p=int(np.argmax(best[n-2])); ch=[]
        for k in range(n-2,-1,-1): ch.append(p); p=arg[k][p]
        ch=ch[::-1]
        for p in ch:
            i,j=P[p]; c=i+int(np.argmin(db[i:j])); cuts.append(c*hop)
    cuts.append(len(a)); res=[]
    for i in range(n):
        seg=a[cuts[i]:cuts[i+1]]; d,_=frames(seg,sr); L=np.where(d>=thr)[0]
        if len(L): seg=seg[max(0,L[0]*hop-int(pad*sr)):min(len(seg),(L[-1]+1)*hop+int(pad*2*sr))]
        sf.write(outs[i],seg,sr); res.append(round(len(seg)/sr,3))
    sp=(s1-s0)/100.0/W.sum(); ratio=[round(r/(w*sp),2) for r,w in zip(res,W)]
    pl=[round((P[p][1]-P[p][0])/100,2) for p in ch] if n>1 else []
    return res,ratio,pl

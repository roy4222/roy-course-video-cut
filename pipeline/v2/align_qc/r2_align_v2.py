"""r2_align_v2 (Reviewer 2026-10-31): re-cue an episode SRT so it never splits ASCII words / code / filenames,
keeps numbers+units together (480萬, 六十三億美元), never leaves a 1-CJK-char cue, max 18 chars/cue.
Timing: lines rebuilt from <ep>.orig.srt.bak (Lead's TTS line timing); per-chunk starts from whisper word
timestamps of the episode's real voice track (rendered mp4 mix; the per-line TTS wavs live on the desktop).
usage: python r2_align_v2.py SECxx   (needs $R2_WORDS_DIR/SECxx.words.json, default /tmp/v2)
Also importable: chunk_v2(text, mx=18)"""
import sys,re,json,difflib,math,os
MX=18
PUN='，。！？；：、,.!?;:…'
NUMU=r'(?:[0-9][0-9,\.]*\s?(?:%|萬|億|千|百|美元|元|個|位元組|位元|秒|分鐘|分|年|月|日|倍|台|人|次|行|格|條|顆|號)*|[零〇一二三四五六七八九十百千萬億兩幾]+(?:\s?(?:%|美元|元|個|位元組|位元|秒|分鐘|年|月|日|倍|台|人|次|行|格|條|顆|號))*)'
TOK=re.compile(r'[-./$~]*[A-Za-z0-9_][A-Za-z0-9_\.\-/+#:@$~\'’]*[A-Za-z0-9_%)]?|'+NUMU+r'|\s+|.',re.S)
def toks(t):
    out=[];i=0
    while i<len(t):
        m=TOK.match(t,i); s=m.group(0) or t[i]; out.append(s); i+=len(s)
    # glue "0x" style, and ASCII token immediately followed by % or 萬 etc. already handled
    return out
core=lambda s: re.sub(r'[\s'+re.escape(PUN)+'「」『』（）()“”"\'—-]','',s)
def L(s): return len(s.strip())
def pack(tk,mx):
    """split token list into pieces <=mx, balanced, breaking only between tokens; prefer after punctuation/space"""
    s=''.join(tk).strip()
    if L(s)<=mx: return [s]
    if L(s)==mx+1 and s[-1] in PUN: return [s[:-1]]
    n=math.ceil(L(s)/mx); tgt=L(s)/n
    # candidate cut positions (token boundaries)
    pos=[];acc=0
    for k,t in enumerate(tk[:-1]):
        acc+=len(t); pos.append((acc,k+1,t))
    best=None
    for acc,k,t in pos:
        left=''.join(tk[:k]).strip()
        if L(left)>mx or L(left)==0: continue
        sc=abs(L(left)-tgt)-(3 if t and t[-1] in PUN else 0)-(1 if t.isspace() else 0)
        right=''.join(tk[k:]).strip()
        if len(core(left))<=1: sc+=50
        if tk[k] in PUN or tk[k][:1] in '」』）)': sc+=100
        if len(core(right))<=3 and L(right)<=mx: sc+=6
        A=lambda x: bool(x) and x.isascii() and x.isalnum()
        if tk[k].isspace() and k+1<len(tk) and A(t[-1:]) and A(tk[k+1][:1]): sc+=6
        if t.isspace() and tk[k-2:k-1] and tk[k-2][-1:].isascii() and tk[k-2][-1:].isalnum() and tk[k][:1].isascii() and tk[k][:1].isalnum(): sc+=6
        if best is None or sc<best[0]: best=(sc,k)
    if best is None:  # a single identifier longer than mx: keep it whole (never split code); hard split only if >24
        if len(tk)==1 and L(s)<=24: return [s]
        big=max(range(len(tk)),key=lambda k:len(tk[k]))
        if len(tk[big])<=24 and len(tk)>1:
            parts=[x for x in (''.join(tk[:big]).strip(), tk[big]+(''.join(tk[big+1:]).strip() if L(tk[big]+''.join(tk[big+1:]))<=mx else '')) if x]
            rest=tk[big+1:] if parts[-1]==tk[big] else []
            return [p_ for q in parts for p_ in (pack(toks(q),mx) if L(q)<=mx or q!=tk[big] else [q])]+(pack(rest,mx) if ''.join(rest).strip() else [])
        return [s[:mx]]+pack(list(s[mx:]),mx)
    k=best[1]; return [''.join(tk[:k]).strip()]+pack(tk[k:],mx)
def chunk_v2(text,mx=MX):
    tk=toks(text.strip())
    # clauses at punctuation
    cl=[];cur=[]
    for t in tk:
        cur.append(t)
        if t in PUN: cl.append(cur);cur=[]
    if cur: cl.append(cur)
    pieces=[]
    for c in cl:
        s=''.join(c).strip()
        if not s: continue
        if pieces and L(pieces[-1])+L(s)<=mx and (L(s)<=5 or L(pieces[-1])<=6 or L(pieces[-1])+L(s)<=14):
            pieces[-1]=pieces[-1]+s if not (pieces[-1][-1:].isascii() and s[:1].isascii() and pieces[-1][-1:].isalnum() and s[:1].isalnum()) else pieces[-1]+' '+s
        else: pieces.extend(pack(c,mx))
    # orphan / punctuation-only merge
    out=[]
    for p in pieces:
        if out and (len(core(p))<=1):
            if L(out[-1])+L(p)<=mx: out[-1]+=p; continue
            # rebalance: steal last token(s) from previous piece
            ptk=toks(out[-1]); moved=[]
            while ptk and (len(core(''.join(moved)+p))<3) and L(''.join(ptk))>3:
                moved.insert(0,ptk.pop())
            out[-1]=''.join(ptk).strip(); p=(''.join(moved)+p).strip()
        out.append(p)
    # leading orphan
    if len(out)>1 and len(core(out[0]))<=1 and L(out[0])+L(out[1])<=mx: out[1]=out[0]+out[1]; out.pop(0)
    return [o for o in out if o]
def ts(t): h,m,s=t.replace(',','.').split(':'); return int(h)*3600+int(m)*60+float(s)
def fmt(t): t=max(0,t); h=int(t//3600); m=int(t%3600//60); s=t%60; return f'{h:02d}:{m:02d}:{s:06.3f}'.replace('.',',')
def read_srt(p):
    cues=[]
    for b in re.split(r'\n\s*\n',open(p,encoding='utf-8-sig').read().strip()):
        x=b.strip().splitlines()
        if len(x)>=3 and '-->' in x[1]:
            a,c=x[1].split('-->'); cues.append([ts(a.strip()),ts(c.strip()),' '.join(x[2:]).strip()])
    return cues
def lines_from(cues):
    """merge cues back into TTS lines: join while the previous does not end a sentence and the gap is small"""
    Ls=[]
    for a,b,t in cues:
        if Ls and not re.search(r'[。！？!?]$',Ls[-1][2]) and a-Ls[-1][1]<0.25:
            p=Ls[-1][2]; sep=' ' if (p[-1:].isascii() and p[-1:].isalnum() and t[:1].isascii() and t[:1].isalnum() and False) else ''
            Ls[-1][1]=b; Ls[-1][2]=p+sep+t
        else: Ls.append([a,b,t])
    return Ls
if __name__=='__main__':
    import opencc; cc=opencc.OpenCC('s2t')
    ep=sys.argv[1]; O=os.path.join(os.environ['SEC_SERIES'], 'out', ep)
    src=f'{O}/{ep}.orig.srt.bak'
    lines=lines_from(read_srt(src))
    words_dir=os.environ.get('R2_WORDS_DIR', '/tmp/v2'); wf=f'{words_dir}/{ep}.words.json'; words=json.load(open(wf)) if os.path.exists(wf) else []
    hc=[];ht=[]
    for a,b,w in words:
        w2=core(cc.convert(w))
        for k,ch in enumerate(w2): hc.append(ch); ht.append(a+(b-a)*k/max(1,len(w2)))
    out=[];nw=0;np_=0
    for i,(t0,t1,text) in enumerate(lines):
        ch=chunk_v2(text)
        ref=core(text)
        lo=next((k for k,t in enumerate(ht) if t>=t0-0.6),len(ht)); hi=next((k for k,t in enumerate(ht) if t>t1+0.6),len(ht))
        sm=difflib.SequenceMatcher(None,ref,hc[lo:hi],autojunk=False); mp={}
        for blk in sm.get_matching_blocks():
            for k in range(blk.size): mp[blk.a+k]=ht[lo+blk.b+k]
        starts=[];idx=0;tot=max(1,len(ref))
        for c in ch:
            n=len(core(c))
            st=mp.get(idx); prop=t0+(t1-t0)*idx/tot
            if st is None or abs(st-prop)>2.5: st=prop; np_+=1
            else: nw+=1
            starts.append(st); idx+=n
        starts[0]=t0
        for k in range(1,len(starts)):
            starts[k]=min(max(starts[k]-0.08,starts[k-1]+0.6),t1-0.3) if t1-starts[k-1]>0.9 else starts[k-1]+0.01
        for k,c in enumerate(ch):
            e=starts[k+1] if k+1<len(ch) else t1
            if len(c)>MX and c[-1] in PUN: c=c[:-1]
            out.append((starts[k],e,c))
    with open(f'{O}/{ep}.v2.srt','w',encoding='utf-8') as f:
        for k,(a,b,c) in enumerate(out,1): f.write(f'{k}\n{fmt(a)} --> {fmt(b)}\n{c}\n\n')
    print(ep,'lines',len(lines),'cues',len(out),'whisper-timed',nw,'proportional',np_)

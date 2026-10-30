"""zh(x): Arabic number -> Chinese reading for narration (e.g. 83.8 -> 八十三點八, 0.375 -> 零點三七五)."""
D='零一二三四五六七八九'
def _int(n):
    n=int(n)
    if n==0: return '零'
    if n<0: return '負'+_int(-n)
    out='';units=[(10000,'萬'),(1000,'千'),(100,'百'),(10,'十')]
    zero=False;started=False
    for u,s in units:
        q=n//u;n%=u
        if q:
            if zero: out+='零';zero=False
            out+=('' if (u==10 and q==1 and not started) else D[q])+s;started=True
        elif started: zero=True
    if n:
        if zero: out+='零'
        out+=D[n]
    return out
def zh(x,nd=None):
    if nd is not None: x=round(x,nd);s=f'{x:.{nd}f}'
    else: s=str(x)
    if s.startswith('-'): return '負'+zh(s[1:])
    if '.' in s:
        a,b=s.split('.');return _int(a)+'點'+''.join(D[int(c)] for c in b)
    return _int(s)
def pct(v,nd=1):
    """0.838 -> 百分之八十三點八"""
    return '百分之'+zh(round(v*100,nd),nd) if nd else '百分之'+zh(round(v*100))
if __name__=='__main__':
    for t in (0,7,10,12,20,24,105,143,569,712,891,1000,0.375,83.8,0.2005):print(t,zh(t))
    print(pct(0.838),pct(0.2005),pct(0.5,0))

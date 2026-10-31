import sys,re,json,os
def _ep(ep):
    return os.path.join(os.environ['SEC_SERIES'], ep)
def load(ep): return open(os.path.join(_ep(ep),'script.md')).read()
def save(ep,t): open(os.path.join(_ep(ep),'script.md'),'w').write(t)
def after(t,anchor,lines):
    a='- '+anchor
    assert t.count(a+'\n')==1,('anchor',anchor,t.count(a+'\n'))
    return t.replace(a+'\n', a+'\n'+''.join('- '+l+'\n' for l in lines),1)
def before(t,anchor,lines):
    a='- '+anchor
    assert t.count(a+'\n')==1,('anchor',anchor)
    return t.replace(a+'\n', ''.join('- '+l+'\n' for l in lines)+a+'\n',1)
def repl(t,old,new):
    assert t.count('- '+old+'\n')==1,('repl',old)
    return t.replace('- '+old+'\n','- '+new+'\n',1)
def scene_before(t,header_prefix,block):
    i=t.index('\n## '+header_prefix)
    return t[:i+1]+block.strip('\n')+'\n\n'+t[i+1:]
def stats(t):
    L=[l[2:] for l in t.splitlines() if l.startswith('- ') and not re.match(r'- (目標長度|定位|鉤子分佈|全部 demo|錄影腳本|視覺類型|只引用|本機 demo|只講)',l)]
    n=sum(len(x) for x in L); long=[x for x in L if len(x)>32]
    return n, round(n/220,1), long, len(re.findall(r'^## ',t,re.M))

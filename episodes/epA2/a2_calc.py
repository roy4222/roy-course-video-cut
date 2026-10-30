import math,json
from collections import Counter
def ent(c):
    n=sum(c);return -sum(x/n*math.log2(x/n) for x in c if x) if n else 0
def gini(c):
    n=sum(c);return 1-sum((x/n)**2 for x in c) if n else 0
CUST=[(1,'M','Family','Small','C0'),(2,'M','Sports','Medium','C0'),(3,'M','Sports','Medium','C0'),(4,'M','Sports','Large','C0'),(5,'M','Sports','Extra Large','C0'),(6,'M','Sports','Extra Large','C0'),(7,'F','Sports','Small','C0'),(8,'F','Sports','Small','C0'),(9,'F','Sports','Medium','C0'),(10,'F','Luxury','Large','C0'),(11,'M','Family','Large','C1'),(12,'M','Family','Extra Large','C1'),(13,'M','Family','Medium','C1'),(14,'M','Luxury','Extra Large','C1'),(15,'F','Luxury','Small','C1'),(16,'F','Luxury','Small','C1'),(17,'F','Luxury','Medium','C1'),(18,'F','Luxury','Medium','C1'),(19,'F','Luxury','Medium','C1'),(20,'F','Luxury','Large','C1')]
CA=['Gender','Car Type','Shirt Size'];CL=['C0','C1']
cust=[dict(ID=r[0],**dict(zip(CA,r[1:4])),cls=r[4]) for r in CUST]
LOAN=[(1,'Yes','Single',125,'No'),(2,'No','Married',100,'No'),(3,'No','Single',70,'No'),(4,'Yes','Married',120,'No'),(5,'No','Divorced',95,'Yes'),(6,'No','Married',60,'No'),(7,'Yes','Divorced',220,'No'),(8,'No','Single',85,'Yes'),(9,'No','Married',75,'No'),(10,'No','Single',90,'Yes')]
LA=['Home Owner','Marital Status','Annual Income'];LCL=['No','Yes']
loan=[dict(ID=r[0],**dict(zip(LA,r[1:4])),cls=r[4]) for r in LOAN]
def cnt(D,cl): c=Counter(r['cls'] for r in D);return [c[k] for k in cl]
def parts(D,a,cont):
    if a in cont:
        vs=sorted({r[a] for r in D});best=None
        return [('cut',(vs[i]+vs[i+1])/2) for i in range(len(vs)-1)]
    return [('multi',None)]
def evaluate(D,a,cl,cont,crit):
    n=len(D);I=ent if crit!='gini' else gini
    par=I(cnt(D,cl));opts=[]
    if a in cont:
        vs=sorted({r[a] for r in D})
        for i in range(len(vs)-1):
            v=(vs[i]+vs[i+1])/2
            ch=[[r for r in D if r[a]<=v],[r for r in D if r[a]>v]]
            opts.append((f'<= {v:g}',[f'<={v:g}',f'>{v:g}'],ch))
    else:
        vals=sorted({r[a] for r in D},key=lambda x:[r[a] for r in D].index(x))
        ch=[[r for r in D if r[a]==v] for v in vals]
        opts.append(('multi',vals,ch))
    res=[]
    for lab,names,ch in opts:
        if len(ch)<2: continue
        w=sum(len(c)/n*I(cnt(c,cl)) for c in ch);gain=par-w
        si=-sum(len(c)/n*math.log2(len(c)/n) for c in ch if c)
        gr=gain/si if si else 0
        score={'gini':gain,'ig':gain,'gr':gr}[crit]
        res.append(dict(attr=a,split=lab,names=names,counts=[cnt(c,cl) for c in ch],ids=[[r['ID'] for r in c] for c in ch],parent=round(par,4),weighted=round(w,4),gain=round(gain,4),splitinfo=round(si,4),gr=round(gr,4),score=score))
    if not res: return None
    return max(res,key=lambda x:x['score']) if a in cont else res[0], res
def hunt(D,attrs,cl,cont,crit,path='root',log=None,depth=0):
    c=cnt(D,cl);node=dict(path=path,counts=c,ids=[r['ID'] for r in D],depth=depth)
    if 0 in c and sum(c)>0 and c.count(0)==len(c)-1:
        node['leaf']=cl[[i for i,x in enumerate(c) if x][0]];log.append(dict(node,cands=None));return node
    cands=[];allc={}
    for a in attrs:
        r=evaluate(D,a,cl,cont,crit)
        if r: cands.append(r[0]);allc[a]=r[1]
    if not cands:
        mx=max(c);node['leaf']=cl[c.index(mx)] if c.count(mx)==1 else 'tie';node['note']='identical attrs';log.append(dict(node,cands=[]));return node
    best=max(cands,key=lambda x:(round(x['score'],10)))
    ties=[x['attr'] for x in cands if abs(x['score']-best['score'])<1e-9]
    node['split']=best;node['ties']=ties;log.append(dict(node,cands=cands,allc={k:v for k,v in allc.items() if k in cont}))
    nxt=[a for a in attrs if a!=best['attr'] or a in cont]
    node['children']=[]
    for nm,ids in zip(best['names'],best['ids']):
        sub=[r for r in D if r['ID'] in ids]
        node['children'].append((nm,hunt(sub,nxt,cl,cont,crit,f"{path} > {best['attr']}={nm}",log,depth+1)))
    return node
def show(log):
    for e in log:
        pre='  '*e['depth']
        if e['cands'] is None: print(pre,e['path'],e['counts'],'LEAF',e['leaf']);continue
        if e['cands']==[]: print(pre,e['path'],e['counts'],'LEAF(no split)',e['leaf'],e['ids']);continue
        print(pre,e['path'],e['counts'],'ties' if len(e['ties'])>1 else '',e['ties'])
        for x in e['cands']: print(pre,'   ',x['attr'],x['split'],x['counts'],'par',x['parent'],'w',x['weighted'],'gain',x['gain'],'SI',x['splitinfo'],'GR',x['gr'])
OUT={}
for name,D,A,cl,cont in [('cust',cust,CA,CL,[]),('loan',loan,LA,LCL,['Annual Income'])]:
    for crit in ['gini','ig','gr']:
        log=[];t=hunt(D,A,cl,cont,crit,log=log);print('=====',name,crit);show(log);OUT[f'{name}_{crit}']=log
json.dump(OUT,open('a2.json','w'),ensure_ascii=False,indent=0,default=str)

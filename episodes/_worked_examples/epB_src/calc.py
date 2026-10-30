from math import log2,sqrt
H=lambda *c: -sum(x/sum(c)*log2(x/sum(c)) for x in c if x)
G=lambda *c: 1-sum((x/sum(c))**2 for x in c)
E=lambda *c: 1-max(c)/sum(c)
print('== EP11 p37')
TP,FN,FP,TN=15,30,50,45;N=TP+FN+FP+TN
P=TP/(TP+FP);Rc=TP/(TP+FN)
for k,v in dict(N=N,ACC=(TP+TN)/N,ERR=(FP+FN)/N,TPR=Rc,TNR=TN/(TN+FP),PPV=P,F1=2*P*Rc/(P+Rc),F1b=2*TP/(2*TP+FP+FN),NPV=TN/(TN+FN),FPR=FP/(FP+TN)).items(): print(k,round(v,4))
print('== EP12 p22')
D=[(1,'p',.9),(2,'p',.8),(3,'n',.7),(4,'p',.6),(5,'p',.55),(6,'p',.54),(7,'n',.53),(8,'n',.52),(9,'p',.51),(10,'n',.5),(11,'p',.4),(12,'n',.39),(13,'p',.38),(14,'n',.37),(15,'n',.36),(16,'n',.35),(17,'p',.34),(18,'n',.33),(19,'p',.3),(20,'n',.1)]
Pn=sum(1 for d in D if d[1]=='p');Nn=20-Pn;print('P',Pn,'N',Nn)
pts=[(0,0,'inf')]
for thr in [d[2] for d in D]:
    tp=sum(1 for d in D if d[2]>=thr and d[1]=='p');fp=sum(1 for d in D if d[2]>=thr and d[1]=='n')
    pts.append((fp/Nn,tp/Pn,thr))
for p in pts: print(p, 'J=%.2f'%(p[1]-p[0]),'d=%.3f'%sqrt(p[0]**2+(1-p[1])**2))
auc=sum((pts[i+1][0]-pts[i][0])*(pts[i+1][1]+pts[i][1])/2 for i in range(len(pts)-1));print('AUC',auc)
# pairwise
pos=[d[2] for d in D if d[1]=='p'];neg=[d[2] for d in D if d[1]=='n'];print('pairwise',sum((a>b)+0.5*(a==b) for a in pos for b in neg)/(len(pos)*len(neg)))
for thr in (0.5,0.54,0.51,0.38,0.34):
    tp=sum(1 for d in D if d[2]>=thr and d[1]=='p');fp=sum(1 for d in D if d[2]>=thr and d[1]=='n');print('thr',thr,'TP',tp,'FP',fp,'FN',Pn-tp,'TN',Nn-fp,'acc',(tp+Nn-fp)/20)
print('== EP14/15 loan')
loan=[(1,'Yes','Single',125,'No'),(2,'No','Married',100,'No'),(3,'No','Single',70,'No'),(4,'Yes','Married',120,'No'),(5,'No','Divorced',95,'Yes'),(6,'No','Married',60,'No'),(7,'Yes','Divorced',220,'No'),(8,'No','Single',85,'Yes'),(9,'No','Married',75,'No'),(10,'No','Single',90,'Yes')]
def cnt(rows): return (sum(r[-1]=='No' for r in rows),sum(r[-1]=='Yes' for r in rows))
print('root (No,Yes)',cnt(loan),'H',H(*cnt(loan)),'G',G(*cnt(loan)),'E',E(*cnt(loan)))
for a,i in (('Home',1),('Mar',2)):
    vals=sorted(set(r[i] for r in loan));ch=[cnt([r for r in loan if r[i]==v]) for v in vals]
    for f,nm in ((H,'H'),(G,'G'),(E,'E')):
        w=sum(sum(c)/10*f(*c) for c in ch);print(a,vals,ch,nm,'children %.4f gain %.4f'%(w,f(*cnt(loan))-w))
    si=H(*[sum(c) for c in ch]);ig=H(*cnt(loan))-sum(sum(c)/10*H(*c) for c in ch);print(a,'splitinfo %.4f gainratio %.4f'%(si,ig/si))
# Hunt steps
no=[r for r in loan if r[1]=='No'];print('HO=No',cnt(no));
for v in ('Single','Divorced','Married'): print(' mar',v,cnt([r for r in no if r[2]==v]))
sd=[r for r in no if r[2] in('Single','Divorced')];print('S/D',cnt(sd),[ (r[0],r[3],r[4]) for r in sd])
print('inc<80',cnt([r for r in sd if r[3]<80]),'>=80',cnt([r for r in sd if r[3]>=80]))
# marital binary gini
for grp in (('Single','Divorced'),('Single',),('Divorced',)):
    A=[r for r in loan if r[2] in grp];B=[r for r in loan if r[2] not in grp];w=len(A)/10*G(*cnt(A))+len(B)/10*G(*cnt(B));print('gini bin',grp,cnt(A),cnt(B),'%.4f'%w)
# continuous
inc=sorted(loan,key=lambda r:r[3]);vs=[r[3] for r in inc]
cuts=[55]+[(vs[i]+vs[i+1])/2 for i in range(9)]+[230]
for t in cuts:
    A=[r for r in loan if r[3]<=t];B=[r for r in loan if r[3]>t]
    w=(len(A)/10*G(*cnt(A)) if A else 0)+(len(B)/10*G(*cnt(B)) if B else 0);print('cut',t,'<=',cnt(A),'>',cnt(B),'gini %.3f'%w)
print('ID gainratio',1/log2(20) if False else None)
print('== A1 data p59/97')
A1=[(1,'M','Family','Small','C0'),(2,'M','Sports','Medium','C0'),(3,'M','Sports','Medium','C0'),(4,'M','Sports','Large','C0'),(5,'M','Sports','Extra Large','C0'),(6,'M','Sports','Extra Large','C0'),(7,'F','Sports','Small','C0'),(8,'F','Sports','Small','C0'),(9,'F','Sports','Medium','C0'),(10,'F','Luxury','Large','C0'),(11,'M','Family','Large','C1'),(12,'M','Family','Extra Large','C1'),(13,'M','Family','Medium','C1'),(14,'M','Luxury','Extra Large','C1'),(15,'F','Luxury','Small','C1'),(16,'F','Luxury','Small','C1'),(17,'F','Luxury','Medium','C1'),(18,'F','Luxury','Medium','C1'),(19,'F','Luxury','Medium','C1'),(20,'F','Luxury','Large','C1')]
c2=lambda rows:(sum(r[-1]=='C0' for r in rows),sum(r[-1]=='C1' for r in rows))
print('root',c2(A1),H(*c2(A1)),G(*c2(A1)))
for nm,i in (('Gender',1),('Car',2),('Shirt',3)):
    vals=sorted(set(r[i] for r in A1));ch=[c2([r for r in A1 if r[i]==v]) for v in vals]
    wh=sum(sum(c)/20*H(*c) for c in ch);wg=sum(sum(c)/20*G(*c) for c in ch);si=H(*[sum(c) for c in ch])
    print(nm,dict(zip(vals,ch)),'Hc %.4f IG %.4f Gc %.4f SI %.4f GR %.4f'%(wh,1-wh,wg,si,(1-wh)/si))
print('ID SI',log2(20),'GR',1/log2(20))
print('impurity N2 (1,5)',G(1,5),H(1,5),E(1,5))

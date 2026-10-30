import json, numpy as np, sys
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
def run(seed,save=False):
    X,y=make_classification(n_samples=600,n_features=6,n_informative=4,n_redundant=0,flip_y=0.12,class_sep=0.9,random_state=seed)
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=0.2,random_state=seed,stratify=y)
    kf=StratifiedKFold(n_splits=3,shuffle=True,random_state=seed)
    res={}
    for d in (2,5,20):
        errs=[]
        for tr,va in kf.split(Xtr,ytr):
            m=DecisionTreeClassifier(max_depth=d,random_state=0).fit(Xtr[tr],ytr[tr]); errs.append(round(1-m.score(Xtr[va],ytr[va]),4))
        res[d]=(errs,round(float(np.mean(errs)),4))
    best=min(res,key=lambda d:res[d][1])
    tests={d:round(1-DecisionTreeClassifier(max_depth=d,random_state=0).fit(Xtr,ytr).score(Xte,yte),4) for d in (2,5,20)}
    if save: json.dump({'cv':{str(k):v for k,v in res.items()},'best':best,'test':tests[best],'n':[len(Xtr),len(Xte)]},open('ep18_cv_check.json','w'))
    return res,best,tests
if len(sys.argv)>1:
    print(run(int(sys.argv[1]),True));sys.exit()
for s in range(40):
    res,best,tests=run(s)
    if best==5 and res[5][1]+0.03<res[2][1] and res[5][1]+0.03<res[20][1] and all(res[5][0][i]<=res[20][0][i] for i in range(3)) and tests[5]<=min(tests.values()):
        print(s,res,tests)

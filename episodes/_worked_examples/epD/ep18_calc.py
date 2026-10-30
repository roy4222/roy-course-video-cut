import json,numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import StratifiedKFold,GridSearchCV,cross_val_score,train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score
R={}
print('p182 cv avg',np.mean([0.2,0.4,0.3]),np.mean([0.4,0.5,0.6]),np.mean([0.4,0.5,0.3]),'p187',np.mean([0.78,0.82,0.80]))
X,y=make_classification(n_samples=600,n_features=6,n_informative=4,n_redundant=0,flip_y=0.12,class_sep=0.9,random_state=7)
# repeated holdout variability
acc=[]
for s in range(5):
    a,b,c,d=train_test_split(X,y,test_size=0.2,random_state=s,stratify=y);acc.append(round(DecisionTreeClassifier(max_depth=5,random_state=0).fit(a,c).score(b,d),4))
R['rep_holdout']=acc;print('holdout acc by seed',acc,np.mean(acc).round(4),np.std(acc).round(4))
# fold-specific vs pooled AUC
kf=StratifiedKFold(3,shuffle=True,random_state=1);aucs=[];oof=np.zeros(len(y))
for tr,va in kf.split(X,y):
    m=DecisionTreeClassifier(max_depth=5,random_state=0).fit(X[tr],y[tr]);p=m.predict_proba(X[va])[:,1];oof[va]=p;aucs.append(round(roc_auc_score(y[va],p),4))
R['fold_auc']=aucs;R['mean_auc']=round(float(np.mean(aucs)),4);R['pooled_auc']=round(roc_auc_score(y,oof),4);print(R)
# nested vs ordinary
grid={'max_depth':[2,5,20]};opt=[];nes=[]
for s in range(5):
    inner=StratifiedKFold(3,shuffle=True,random_state=s);outer=StratifiedKFold(3,shuffle=True,random_state=100+s)
    g=GridSearchCV(DecisionTreeClassifier(random_state=0),grid,cv=inner).fit(X,y);opt.append(g.best_score_)
    nes.append(cross_val_score(GridSearchCV(DecisionTreeClassifier(random_state=0),grid,cv=inner),X,y,cv=outer).mean())
R['ordinary']=round(float(np.mean(opt)),4);R['nested']=round(float(np.mean(nes)),4);print('ordinary best cv acc',R['ordinary'],'nested',R['nested'])
json.dump(R,open('ep18_calc.json','w'))

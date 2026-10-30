import json,numpy as np,pandas as pd,seaborn as sns
from sklearn.model_selection import train_test_split,StratifiedKFold,cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,roc_auc_score,roc_curve
R={}
df=sns.load_dataset('titanic')
R['shape']=list(df.shape);R['cols']=list(df.columns)
R['na']={c:int(v) for c,v in df.isna().sum().items() if v>0}
R['surv_rate']=round(df.survived.mean(),4);R['n_surv']=int(df.survived.sum())
R['by_sex']=df.groupby('sex').survived.mean().round(4).to_dict()
R['by_class']={str(k):v for k,v in df.groupby('pclass').survived.mean().round(4).to_dict().items()}
R['n_sex']=df.sex.value_counts().to_dict();R['n_class']={str(k):int(v) for k,v in df.pclass.value_counts().to_dict().items()}
R['age_desc']=df.age.describe().round(2).to_dict();R['fare_desc']=df.fare.describe().round(2).to_dict()
R['age_hist']=np.histogram(df.age.dropna(),bins=range(0,90,10))[0].tolist()
df['agebin']=pd.cut(df.age,[0,12,18,40,60,100])
R['by_age']={str(k):round(v,4) for k,v in df.groupby('agebin',observed=False).survived.mean().items()}
R['alive_eq']=bool(((df.alive=='yes')==(df.survived==1)).all())
y=df.survived.values
SEED=1
idx=np.arange(len(df))
tr,te=train_test_split(idx,test_size=0.2,random_state=SEED,stratify=y)
R['split']=[len(tr),len(te)]
# BEFORE: raw numeric columns only, NaN left as is (tree handles NaN natively in sklearn>=1.3)
def X_before(d): return d[['pclass','age','sibsp','parch','fare']].values.astype(float)
# AFTER: fit preprocessing on training part only
def prep_fit(d):
    return dict(age_med=d.groupby(['sex','pclass']).age.median().to_dict(),emb_mode=d.embarked.mode()[0],fare_med=d.fare.median())
def X_after(d,P):
    o=pd.DataFrame(index=d.index)
    age=d.age.copy();m=age.isna()
    age[m]=[P['age_med'][(s,c)] for s,c in zip(d.sex[m],d.pclass[m])]
    o['pclass']=d.pclass;o['sex_male']=(d.sex=='male').astype(int);o['age']=age
    o['family']=d.sibsp+d.parch;o['alone']=(o.family==0).astype(int);o['fare_log']=np.log1p(d.fare.fillna(P['fare_med']))
    emb=d.embarked.fillna(P['emb_mode'])
    for e in ['C','Q','S']: o['emb_'+e]=(emb==e).astype(int)
    return o
P=prep_fit(df.iloc[tr]);R['prep']=dict(age_med={f'{k[0]}-{k[1]}':v for k,v in P['age_med'].items()},emb_mode=P['emb_mode'])
XA=X_after(df,P);R['after_cols']=list(XA.columns);XA=XA.values.astype(float);XB=X_before(df)
R['after_head']=X_after(df.head(3),P).round(3).values.tolist()
DEPTH=[3,5,None];LEAF=[1,5,20]
def grid_hh(X,seeds=(1,10,100)):
    out={}
    for d in DEPTH:
        for l in LEAF:
            errs=[];terr=[]
            for s in seeds:
                a,b=train_test_split(tr,test_size=0.2,random_state=s,stratify=y[tr])
                m=DecisionTreeClassifier(max_depth=d,min_samples_leaf=l,random_state=0).fit(X[a],y[a])
                errs.append(round(1-m.score(X[b],y[b]),4));terr.append(round(1-m.score(X[a],y[a]),4))
            out[f'{d}|{l}']=dict(val=errs,val_mean=round(float(np.mean(errs)),4),train_mean=round(float(np.mean(terr)),4))
    return out
def grid_cv(X,seed=1):
    out={};kf=StratifiedKFold(3,shuffle=True,random_state=seed)
    for d in DEPTH:
        for l in LEAF:
            errs=[];terr=[]
            for a,b in kf.split(tr,y[tr]):
                a=tr[a];b=tr[b];m=DecisionTreeClassifier(max_depth=d,min_samples_leaf=l,random_state=0).fit(X[a],y[a])
                errs.append(round(1-m.score(X[b],y[b]),4));terr.append(round(1-m.score(X[a],y[a]),4))
            out[f'{d}|{l}']=dict(val=errs,val_mean=round(float(np.mean(errs)),4),train_mean=round(float(np.mean(terr)),4))
    return out
def best(g): return min(g,key=lambda k:(g[k]['val_mean'],k))
def final(X,key):
    d,l=key.split('|');d=None if d=='None' else int(d);l=int(l)
    m=DecisionTreeClassifier(max_depth=d,min_samples_leaf=l,random_state=0).fit(X[tr],y[tr])
    p=m.predict(X[te]);pr=m.predict_proba(X[te])[:,1];tn,fp,fn,tp=confusion_matrix(y[te],p).ravel()
    fpr,tpr,_=roc_curve(y[te],pr)
    return dict(train_err=round(1-m.score(X[tr],y[tr]),4),test_err=round(1-accuracy_score(y[te],p),4),acc=round(accuracy_score(y[te],p),4),
        sens=round(float(tp/(tp+fn)),4),spec=round(float(tn/(tn+fp)),4),auc=round(roc_auc_score(y[te],pr),4),cm=[int(tp),int(fn),int(fp),int(tn)],
        roc=[[round(a,4),round(b,4)] for a,b in zip(fpr,tpr)],leaves=int(m.get_n_leaves()),depth=int(m.get_depth()))
for name,X in (('before',XB),('after',XA)):
    hh=grid_hh(X);cv=grid_cv(X);bh=best(hh);bc=best(cv)
    R[name]=dict(hh=hh,cv=cv,best_hh=bh,best_cv=bc,final_hh=final(X,bh),final_cv=final(X,bc))
# repeat whole holdout+CV pipeline with different outer seeds (after)
rep={}
for s in (1,10,100):
    t2,e2=train_test_split(idx,test_size=0.2,random_state=s,stratify=y);P2=prep_fit(df.iloc[t2]);X2=X_after(df,P2).values.astype(float)
    kf=StratifiedKFold(3,shuffle=True,random_state=s);g={}
    for d in DEPTH:
        for l in LEAF:
            sc=[]
            for a,b in kf.split(t2,y[t2]):
                m=DecisionTreeClassifier(max_depth=d,min_samples_leaf=l,random_state=0).fit(X2[t2[a]],y[t2[a]]);sc.append(1-m.score(X2[t2[b]],y[t2[b]]))
            g[f'{d}|{l}']=float(np.mean(sc))
    k=min(g,key=lambda k:(g[k],k));d,l=k.split('|');m=DecisionTreeClassifier(max_depth=None if d=='None' else int(d),min_samples_leaf=int(l),random_state=0).fit(X2[t2],y[t2])
    rep[s]=dict(best=k,cv=round(g[k],4),test_acc=round(m.score(X2[e2],y[e2]),4),auc=round(roc_auc_score(y[e2],m.predict_proba(X2[e2])[:,1]),4))
R['repeat']=rep
# majority baseline
R['baseline_acc']=round(max(y[te].mean(),1-y[te].mean()),4)
json.dump(R,open('a3.json','w'),ensure_ascii=False,indent=1,default=str)
for k in ('shape','na','surv_rate','by_sex','by_class','by_age','alive_eq','split','prep','after_cols','baseline_acc','repeat'): print(k,R[k])
for n in ('before','after'):
    print('==',n,'best_hh',R[n]['best_hh'],'best_cv',R[n]['best_cv'])
    for k,v in R[n]['hh'].items(): print(' hh',k,v)
    for k,v in R[n]['cv'].items(): print(' cv',k,v)
    for f in ('final_hh','final_cv'): print(f,{k:v for k,v in R[n][f].items() if k!='roc'})

import json
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
X,y=make_classification(n_samples=500,n_features=6,n_informative=4,n_redundant=0,flip_y=0.1,class_sep=0.9,random_state=7)
Xtr,Xva,ytr,yva=train_test_split(X,y,test_size=0.2,random_state=7)
r={}
for d in range(1,21):
    m=DecisionTreeClassifier(max_depth=d,random_state=0).fit(Xtr,ytr); r[d]=[round(1-m.score(Xtr,ytr),4),round(1-m.score(Xva,yva),4),int(m.get_n_leaves())]
json.dump(r,open('ep17_curve.json','w'));print(r[2],r[5],r[20],len(Xtr),len(Xva))
print({d:r[d] for d in r})

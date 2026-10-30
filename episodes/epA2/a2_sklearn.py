import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_text
from a2_hunt import CUSTOMER, LOAN
loan = pd.DataFrame(LOAN, columns=['ID','HomeOwner','Marital','Income','Default'])
X = pd.get_dummies(loan[['HomeOwner','Marital','Income']], dtype=int)
y = loan['Default']
for crit in ['gini', 'entropy']:
    t = DecisionTreeClassifier(criterion=crit, random_state=0).fit(X, y)
    print(f'--- loan | criterion={crit} | leaves={t.get_n_leaves()} depth={t.get_depth()} acc={t.score(X, y):.2f}')
    print(export_text(t, feature_names=list(X.columns)))
cust = pd.DataFrame(CUSTOMER, columns=['ID','Gender','CarType','ShirtSize','Class'])
Xc = pd.get_dummies(cust[['Gender','CarType','ShirtSize']], dtype=int)
for crit in ['gini', 'entropy']:
    t = DecisionTreeClassifier(criterion=crit, random_state=0).fit(Xc, cust['Class'])
    print(f'--- customer | criterion={crit} | leaves={t.get_n_leaves()} depth={t.get_depth()} acc={t.score(Xc, cust["Class"]):.2f}')
    print(export_text(t, feature_names=list(Xc.columns)))

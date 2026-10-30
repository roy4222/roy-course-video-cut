# Assignment 2 demo: Hunt's algorithm with Gini / Information Gain / Gain Ratio (from scratch)
import math
from collections import Counter

def entropy(c):
    n = sum(c); return -sum(x/n*math.log2(x/n) for x in c if x)
def gini(c):
    n = sum(c); return 1 - sum((x/n)**2 for x in c)

def counts(D, classes): c = Counter(r['cls'] for r in D); return [c[k] for k in classes]

def candidates(D, a, numeric):
    """yield (label, [child record lists]) for attribute a"""
    if a in numeric:                                  # continuous: binary split at midpoints
        vs = sorted({r[a] for r in D})
        for i in range(len(vs) - 1):
            v = (vs[i] + vs[i+1]) / 2
            yield f'<={v:g}', [[r for r in D if r[a] <= v], [r for r in D if r[a] > v]], [f'<={v:g}', f'>{v:g}']
    else:                                             # categorical: multi-way split
        vals = list(dict.fromkeys(r[a] for r in D))
        if len(vals) > 1:
            yield 'multi', [[r for r in D if r[a] == v] for v in vals], vals

def score(D, kids, classes, crit):
    n = len(D); I = gini if crit == 'gini' else entropy
    w = sum(len(k)/n * I(counts(k, classes)) for k in kids)
    delta = I(counts(D, classes)) - w
    split_info = -sum(len(k)/n * math.log2(len(k)/n) for k in kids)
    return (delta / split_info if crit == 'gain_ratio' else delta), w, delta, split_info

def hunt(D, attrs, classes, numeric, crit, path='root', depth=0):
    c = counts(D, classes); pad = '  ' * depth
    print(f'{pad}[{path}] n={len(D)} counts={tuple(c)} IDs={[r["ID"] for r in D]}')
    if sum(1 for x in c if x) == 1:
        print(f'{pad}  -> LEAF {classes[c.index(max(c))]} (pure)'); return
    best = None
    for a in attrs:
        for lab, kids, names in candidates(D, a, numeric):
            s, w, d, si = score(D, kids, classes, crit)
            print(f'{pad}  {a:15s} {lab:9s} kids={[tuple(counts(k, classes)) for k in kids]} '
                  f'I(children)={w:.4f} delta={d:.4f} SplitInfo={si:.4f} score={s:.4f}')
            if best is None or s > best[0] + 1e-12:   # ties keep the earlier column
                best = (s, a, kids, names)
    if best is None:                                  # identical attribute values
        m = max(c); lab = classes[c.index(m)] if c.count(m) == 1 else 'tie -> parent majority'
        print(f'{pad}  -> LEAF {lab} (cannot split)'); return
    s, a, kids, names = best
    print(f'{pad}  => SPLIT on {a} ({crit} = {s:.4f})')
    for nm, k in zip(names, kids):
        hunt(k, attrs, classes, numeric, crit, f'{path} > {a}={nm}', depth + 1)

CUSTOMER = [(1,'M','Family','Small','C0'),(2,'M','Sports','Medium','C0'),(3,'M','Sports','Medium','C0'),
 (4,'M','Sports','Large','C0'),(5,'M','Sports','Extra Large','C0'),(6,'M','Sports','Extra Large','C0'),
 (7,'F','Sports','Small','C0'),(8,'F','Sports','Small','C0'),(9,'F','Sports','Medium','C0'),
 (10,'F','Luxury','Large','C0'),(11,'M','Family','Large','C1'),(12,'M','Family','Extra Large','C1'),
 (13,'M','Family','Medium','C1'),(14,'M','Luxury','Extra Large','C1'),(15,'F','Luxury','Small','C1'),
 (16,'F','Luxury','Small','C1'),(17,'F','Luxury','Medium','C1'),(18,'F','Luxury','Medium','C1'),
 (19,'F','Luxury','Medium','C1'),(20,'F','Luxury','Large','C1')]
LOAN = [(1,'Yes','Single',125,'No'),(2,'No','Married',100,'No'),(3,'No','Single',70,'No'),
 (4,'Yes','Married',120,'No'),(5,'No','Divorced',95,'Yes'),(6,'No','Married',60,'No'),
 (7,'Yes','Divorced',220,'No'),(8,'No','Single',85,'Yes'),(9,'No','Married',75,'No'),(10,'No','Single',90,'Yes')]
cust = [dict(ID=r[0], Gender=r[1], CarType=r[2], ShirtSize=r[3], cls=r[4]) for r in CUSTOMER]
loan = [dict(ID=r[0], HomeOwner=r[1], Marital=r[2], Income=r[3], cls=r[4]) for r in LOAN]

if __name__ == '__main__':
    for crit in ['gini', 'info_gain', 'gain_ratio']:
        print(f'\n===== customer data | {crit} =====')
        hunt(cust, ['Gender', 'CarType', 'ShirtSize'], ['C0', 'C1'], [], crit)
    for crit in ['gini', 'info_gain', 'gain_ratio']:
        print(f'\n===== loan data | {crit} =====')
        hunt(loan, ['HomeOwner', 'Marital', 'Income'], ['No', 'Yes'], ['Income'], crit)

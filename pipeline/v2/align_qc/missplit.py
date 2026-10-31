import json,sys,glob,os
def nm(s): return ''.join(ch for ch in s if ch.isalnum()).lower()
for n in sys.argv[1:]:
    q=f'SEC{n}/qc'; p=q+'/qc/r2_align_stats.json'
    if not os.path.exists(p): p=q+'/r2_align_stats.json'
    A=json.load(open(p)); S={l['id']:l for l in json.load(open(q+'/script.json'))}; ids=[l['id'] for l in json.load(open(q+'/script.json'))]
    bad=[]
    for i,a in enumerate(A):
        h=nm(a['heard'])
        if len(h)<3: continue
        for j in (i-1,i+1):
            if 0<=j<len(ids):
                nb=nm(S[ids[j]].get('say') or S[ids[j]]['text']); own=nm(S[ids[i]].get('say') or S[ids[i]]['text'])
                # any 4-char chunk of neighbor in heard and not in own
                if any(nb[k:k+4] in h and nb[k:k+4] not in own for k in range(0,max(1,len(nb)-3))): bad.append(a['id']); break
    print('SEC'+n,len(bad),bad)

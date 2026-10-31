import sys,re,os
ep,txt=sys.argv[1],sys.argv[2]
p=os.path.join(os.environ.get('SEC_SERIES','.'),'STATUS.md');s=open(p).read()
old=f"| {ep} | 👷 executor-HX3 認領 11:40 |"
assert old in s
s=s.replace(old,f"| {ep} | ✅ READY {txt} |");open(p,'w').write(s)

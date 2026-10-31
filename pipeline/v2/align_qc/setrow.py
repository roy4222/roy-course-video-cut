# setrow.py SEC11 "| SEC11 | ... |"  -> replace the table row starting with "| SEC11 |"
import sys,re,time,os
p=os.path.join(os.environ['SEC_SERIES'],'STATUS.md'); k,new=sys.argv[1],sys.argv[2]
L=open(p,encoding='utf-8').read().split('\n')
hit=[i for i,l in enumerate(L) if l.startswith(f'| {k} |')]
assert len(hit)==1,hit
L[hit[0]]=new
L=[re.sub(r'^更新：[0-9-]+ [0-9:]+',time.strftime('更新：%F %H:%M'),l) for l in L]
open(p,'w',encoding='utf-8').write('\n'.join(L)); print('ok',k)

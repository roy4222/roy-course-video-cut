import re,sys,os,time
p=os.path.join(os.environ['SEC_SERIES'],'STATUS.md'); s=open(p).read()
for n in sys.argv[1:]:
    n=int(n)
    s2=re.sub(r'^\| SEC%d \| ✅ READY'%n, '| SEC%d | ⛔ ENHANCING (do not render) — enhancer %s；ep 內 build.py/film_media 為 v1，完成後 enhancer 會重跑 md2build｜原註：'%(n,time.strftime('%H:%M')), s, count=1, flags=re.M)
    assert s2!=s,n; s=s2
    d=os.path.join(os.environ['SEC_SERIES'], f'ep{n}')
    os.rename(d+'/READY',d+'/READY.v1hold')
    for f in ['script.md','meta.json']:
        b=d+'/'+f.replace('.','.v1.')
        if not os.path.exists(b): os.system(f'cp {d}/{f} {b}')
open(p,'w').write(s)

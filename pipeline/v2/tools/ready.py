import re,sys,os,time
n=int(sys.argv[1]); note=sys.argv[2]
p=os.path.join(os.environ['SEC_SERIES'],'STATUS.md'); s=open(p).read()
s2=re.sub(r'^\| SEC%d \| ⛔ ENHANCING \(do not render\)[^|]*'%n, '| SEC%d | ✅ READY v2 %s（%s；v1 備份 script.v1.md） '%(n,time.strftime('%H:%M'),note), s, flags=re.M)
assert s2!=s; open(p,'w').write(s2)
d=os.path.join(os.environ['SEC_SERIES'], f'ep{n}'); open(d+'/READY','w').close()
if os.path.exists(d+'/READY.v1hold'): os.remove(d+'/READY.v1hold')

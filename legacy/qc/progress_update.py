import json,os,sys,time,fcntl
f,ep,kw=sys.argv[1],sys.argv[2],json.loads(sys.argv[3])
VS=os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style');p=f'{VS}/{f}'
lk=open(f'{VS}/progress_D.lock' if 'D' in f else p+'.lock','w');fcntl.flock(lk,fcntl.LOCK_EX)
P=json.load(open(p));e=P.setdefault(ep,{});e.update(kw);e['updated']=time.strftime('%Y-%m-%d %H:%M')
json.dump(P,open(p+'.tmp','w'),ensure_ascii=False,indent=1);os.replace(p+'.tmp',p);print(json.dumps(P[ep],ensure_ascii=False))

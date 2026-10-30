import json,fcntl,sys,os
e,mp4,srt=sys.argv[1:4]
root=os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style')
f=open(root+'/progress_A.json.lock','w'); fcntl.flock(f,2)
P=json.load(open(root+'/progress_A.json'))
d=P.setdefault(e,{}).setdefault('drive',{}); d['mp4']=mp4; d['srt']=srt; d['done']=True
json.dump(P,open(root+'/progress_A.json','w'),ensure_ascii=False,indent=1); print(e,P[e].keys())

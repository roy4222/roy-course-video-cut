# recframes.py OUTDIR NN -> qc/rec_montage.jpg : frames at start+3s, mid, end-0.8s of each scene that uses rec/
import json,sys,subprocess,os
O,N=sys.argv[1],sys.argv[2]; q=O+'/qc'
S=json.load(open(q+'/script.json')); C=json.load(open(q+'/cues.json')); sc=json.load(open(q+'/scenes.json'))
ts=[];
for x in sc:
  if 'rec/' not in json.dumps(x['els']): continue
  idx=[i for i,l in enumerate(S) if l['sc']==x['id']]
  if not idx: continue
  a,b=C[idx[0]]['t0'],C[idx[-1]]['t1']
  ts+= [(x['id'],a+3),(x['id'],(a+b)/2),(x['id'],b-0.8)]
fs=[]
for k,(i,t) in enumerate(ts):
  f=f'{q}/rf{k:02d}.jpg'; subprocess.run(['ffmpeg','-loglevel','error','-y','-ss',str(t),'-i',f'{O}/SEC{N}.mp4','-frames:v','1','-vf','scale=480:-2',f],check=True); fs.append(f)
cols=3; rows=(len(fs)+cols-1)//cols
while len(fs)<rows*cols: fs.append(fs[-1])
args=sum([['-i',f] for f in fs],[])
lay='|'.join(f'{(k%cols)*480}_{(k//cols)*270}' for k in range(len(fs)))
subprocess.run(['ffmpeg','-loglevel','error','-y']+args+['-filter_complex',f'xstack=inputs={len(fs)}:layout={lay}',q+'/rec_montage.jpg'],check=True)
for f in fs: os.path.exists(f) and os.remove(f)
print(len(ts)//3,'rec scenes', [i for i,_ in ts[::3]])

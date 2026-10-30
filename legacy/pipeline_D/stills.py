"""stills.py <epdir> [scene ids...]: render end-of-scene stills + contact sheets into qc/pre"""
import json,os,sys,subprocess
LEMO=os.environ.get('LEMO_OPUSCAR','/workspace/video_style/lemo-opuscar')
D=os.path.abspath(sys.argv[1]);only=sys.argv[2:]
L=json.loads(open(D+'/film/timeline.js').read().split('window.LINES=')[1].split(';\nwindow.SCENES')[0])
order=[];last={}
for l in L:
    if l['sc'] not in order: order.append(l['sc'])
    last[l['sc']]=l['t1']
ts=[(sc,round(last[sc]-0.3,2)) for sc in order if not only or sc in only]
out=D+'/qc/pre';os.makedirs(out,exist_ok=True);subprocess.run('rm -f '+out+'/*.jpg',shell=True)
subprocess.run(['node','core/render/still.mjs',D+'/film',*[str(t) for _,t in ts],'--out',out,'--prefix','s_'],cwd=LEMO,check=True,capture_output=True)
from PIL import Image
fs=[f'{out}/s_{t}.jpg' for _,t in ts]
for k in range(0,len(fs),4):
    S=Image.new('RGB',(1928,1088),'#333')
    for i,f in enumerate(fs[k:k+4]):
        im=Image.open(f).resize((960,540));S.paste(im,((i%2)*968,(i//2)*548))
    S.save(f'{out}/sheet{k//4}.jpg',quality=88)
print(out,[sc for sc,_ in ts])

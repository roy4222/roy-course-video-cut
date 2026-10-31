import json,sys,os,shutil,re,datetime
ep,meta,credits,rec,lab,disp=sys.argv[1],json.loads(open(sys.argv[2]).read()),json.loads(open(sys.argv[3]).read()),sys.argv[4],sys.argv[5],sys.argv[6]
d=f'ep{ep}'
json.dump(meta,open(f'{d}/meta.json','w'),ensure_ascii=False,indent=1)
for k,v in credits.items(): open(f'{d}/assets/{k}.credit.txt','w').write(v+'（擷取 2026-10-31）\n')
for f in os.listdir(f'{d}/assets'):
    if f.endswith('.png'): assert os.path.exists(f'{d}/assets/'+f[:-4]+'.credit.txt'),f
    assert f.isascii(),f
shutil.copy(f'lab/rec/{rec}.sh',f'{d}/recordings/{rec}.sh'); shutil.copy('lab/rec/hxrec.sh',f'{d}/recordings/hxrec.sh')
open(f'{d}/recordings/{rec}.credit.txt','w').write(f'本機錄影（Xvfb :{disp}），2026-10-31；腳本 recordings/{rec}.sh（錄製器 hxrec.sh，.cast 為 asciinema 同步檔）；素材 {lab}（自己的玩具環境，只連 127.0.0.1）；無真實目標\n')
s=open(f'{d}/script.md').read()
L=[l[2:] for l in s.split('## 00')[1].splitlines() if l.startswith('- ')]
assert max(map(len,L))<=45
for a in re.findall(r'assets/[\w.]+',s): assert os.path.exists(f'{d}/{a}'),a
assert os.path.exists(f'{d}/recordings/{rec}.mp4')
open(f'{d}/READY','w').close()
print(ep,len(L),'lines',sum(map(len,L)),'chars')

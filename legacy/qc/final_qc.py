import sys,json,subprocess,re,numpy as np,os
_root=os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style'); e=sys.argv[1]; d=f'{_root}/{e}'; mp=f'{d}/{e}.mp4'
p=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height,r_frame_rate','-of','json',mp],capture_output=True,text=True).stdout)
r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',mp,'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True).stderr
I=float(re.findall(r'I:\s+(-?[\d.]+) LUFS',r)[-1]);P=float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS',r)[-1])
def ts(s):h,m,x=s.split(':');x,ms=x.split(',');return int(h)*3600+int(m)*60+int(x)+int(ms)/1000
cues=[(ts(a),ts(b)) for a,b in re.findall(r'(\d\d:\d\d:\d\d,\d+) --> (\d\d:\d\d:\d\d,\d+)',open(f'{d}/{e}.srt',encoding='utf-8').read())]
dur=float(p['format']['duration'])
sr=16000;a=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',mp,'-ac','1','-ar',str(sr),'-f','s16le','-'],capture_output=True).stdout,dtype=np.int16).astype(np.float32)/32768
hop=160;rms=np.sqrt(np.convolve(a**2,np.ones(400)/400,'same')[::hop]);thr=0.02
offs=[]
for k in np.linspace(5,len(cues)-5,6).astype(int):
    t0,t1=cues[k];i0=int((t0-0.6)*100);seg=rms[i0:int((t0+1.5)*100)]
    on=np.argmax(seg>thr)/100+(t0-0.6) if (seg>thr).any() else None
    # end: last loud frame before next cue
    offs.append((round(t0,1),round(on-t0,2) if on is not None else None))
v=[s for s in p['streams'] if s['codec_name']=='h264'][0]
print(json.dumps(dict(ep=e,w=v['width'],h=v['height'],fps=v['r_frame_rate'],dur=round(dur,2),last_cue_end=cues[-1][1],dur_minus_cue=round(dur-cues[-1][1],2),lufs=I,tp=P,onsets=offs)))

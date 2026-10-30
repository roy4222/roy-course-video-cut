import json,sys,os,subprocess,time
_vt=os.environ.get('VOICE_TEST')
if not _vt:
    _c=os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','legacy','tools','voice_test'))
    _vt=_c if os.path.isdir(_c) else '/workspace/video_style/voice_test'
sys.path.insert(0,_vt); import gem
L=json.load(open('lines.json'))
costs=json.load(open('voice_enc/costs.json')) if os.path.exists('voice_enc/costs.json') else {}
for l in L:
    out=f"voice_enc/{l['id']}.wav"
    if os.path.exists(out): continue
    text=l.get('say') or l['text']
    g=gem.synth(text,out+'.tmp.wav',tries=12)
    # trim leading/trailing silence
    subprocess.run(['ffmpeg','-loglevel','error','-y','-i',out+'.tmp.wav','-af','silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.08,areverse','-ar','24000','-ac','1',out],check=True)
    os.remove(out+'.tmp.wav')
    costs[l['id']]=gem.cost(g) if g else None
    json.dump(costs,open('voice_enc/costs.json','w'))
    print(l['id'],costs[l['id']],flush=True)
    time.sleep(1)
import soundfile as sf
dur={l['id']:round(sf.info(f"voice_enc/{l['id']}.wav").duration,3) for l in L}
json.dump(dur,open('voice_enc/dur.json','w'),indent=0)
print('TOTAL dur',sum(dur.values()),'cost',sum(v or 0 for v in costs.values()))

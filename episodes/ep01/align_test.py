import json
from faster_whisper import WhisperModel
from align_split import split_scene
S=json.load(open('script.json')); m=WhisperModel('small',device='cpu',compute_type='int8')
import os; _al=os.environ.get('ALIGN_TMP','/tmp/al'); os.makedirs(_al,exist_ok=True)
for sc in ['title','hook','rules','paradigm','define']:
    L=[l for l in S if l['sc']==sc]
    r,h=split_scene(m,f'voice_enc/scenes/{sc}.wav',[l.get('say') or l['text'] for l in L],[f"{_al}/{l['id']}.wav" for l in L])
    print(sc,[(x['dur'],x['match']) for x in r]); print('  ',h[:200])

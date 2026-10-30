import json,opencc
from faster_whisper import WhisperModel
cc=opencc.OpenCC('s2t')
S=json.load(open('script.json')); M=json.load(open('voice_enc/match.json'))
m=WhisperModel('small',device='cpu',compute_type='int8')
for l in S:
    if M[l['id']]<0.95:
        segs,_=m.transcribe(f"voice_enc/{l['id']}.wav",language='zh',vad_filter=True,initial_prompt='以下是繁體中文的句子。')
        print(l['id'],M[l['id']],'\n  稿:',l.get('say') or l['text'],'\n  聽:',cc.convert(''.join(s.text for s in segs)))

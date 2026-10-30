import sys
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device='cpu',compute_type='int8')
for f in sys.argv[2:]:
    segs,info=m.transcribe(f,language='zh',vad_filter=True,initial_prompt='以下是繁體中文的句子。')
    print('##',f,round(info.duration,1)); print(''.join(s.text for s in segs))

import sys
from faster_whisper import WhisperModel
m=WhisperModel("small",device="cpu",compute_type="int8",cpu_threads=8)
for id,dur in [("McNRkd5CxFY",150),("u0yKHP0onwU",150),("4Ylr5S60YJ4",420),("K9kk0e5xgCI",200),("IlNOhNeWGgY",110),("L1eDBgdCmuU",120),("4gciWspBVHw",100)]:
    import subprocess
    subprocess.run(["ffmpeg","-loglevel","error","-y","-t",str(dur),"-i",f"{id}/video.webm","-ac","1","-ar","16000",f"{id}/a.wav"])
    segs,_=m.transcribe(f"{id}/a.wav",language="zh",vad_filter=True)
    with open(f"{id}/transcript.txt","w") as f:
        for s in segs: f.write(f"[{s.start:6.1f}] {s.text}\n")
    print(id,"done",flush=True)

import json,sys,os
ep,title,vid,status=sys.argv[1:5]
here=os.path.dirname(os.path.abspath(__file__))
p=os.environ.get('YOUTUBE_UPLOADS_JSON')
if not p:
    local=os.path.join(here,'youtube_uploads.json')
    legacy=os.path.join(os.environ.get('VIDEO_STYLE_ROOT','/workspace/video_style'),'youtube_uploads.json')
    p=local if os.path.exists(local) else legacy
d=json.load(open(p))
d.append({"episode":ep,"title":title,"video_id":vid,"url":f"https://youtu.be/{vid}","status":status,"visibility":"private","machine":"<mac-hostname>","uploaded_at":"2026-10-30 (Asia/Taipei)"})
json.dump(d,open(p,'w'),ensure_ascii=False,indent=1); print(len(d))

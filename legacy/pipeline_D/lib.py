"""Episode DSL: ep=Ep(11,...); ep.scene('hook','標題'); i=ep.L('句子'); ep.E('card',...); ep.save()"""
import json,os
class Ep:
    def __init__(self,num,title,head,summary,tags,nxt,accent='A'):
        self.num=num;self.title=title;self.head=head;self.summary=summary;self.tags=tags;self.next=nxt;self.accent=accent
        self.lines=[];self.scenes=[];self.cur=None
    def scene(self,id,title,tag=None,desc='',ref='',chapter=None,noHeader=False,tagCol=None):
        sc=dict(id=id,title=title,els=[],desc=desc,ref=ref,chapter=chapter or title)
        if tag: sc['tag']=tag
        if tagCol: sc['tagCol']=tagCol
        if noHeader: sc['noHeader']=True
        self.scenes.append(sc);self.cur=sc;self.n=0;return sc
    def L(self,text,say=None,gap=0.0):
        self.lines.append(dict(sc=self.cur['id'],text=text,say=say,gap=gap));self.n+=1;return self.n-1
    def E(self,type,**kw):
        kw['type']=type;self.cur['els'].append(kw);return kw
    def save(self,d):
        os.makedirs(d,exist_ok=True)
        for i,l in enumerate(self.lines): l['id']=f'l{i:03d}'
        json.dump(self.lines,open(f'{d}/script.json','w'),ensure_ascii=False,indent=0)
        json.dump([{'id':l['id'],'sc':l['sc'],'text':l['text'],**({'say':l['say']} if l['say'] else {})} for l in self.lines],open(f'{d}/lines.json','w'),ensure_ascii=False,indent=0)
        json.dump(self.scenes,open(f'{d}/scenes.json','w'),ensure_ascii=False)
        json.dump(dict(num=self.num,title=self.title,head=self.head,summary=self.summary,tags=self.tags,next=self.next,accent=self.accent),open(f'{d}/meta.json','w'),ensure_ascii=False,indent=1)
        n=sum(len(l['text']) for l in self.lines)
        print(f'EP{self.num:02d}: {len(self.lines)} lines, {len(self.scenes)} scenes, {n} chars, est {n*0.27/60:.1f} min')
        for sc in self.scenes:
            L=[l for l in self.lines if l['sc']==sc['id']]
            assert L, 'empty scene '+sc['id']
            def chk(x):
                if isinstance(x,dict):
                    for kk,v in x.items():
                        if kk in('at','until','qi','ai','hot','oat') and v is not None:
                            i=v[0] if isinstance(v,list) else v
                            assert -1<=i<len(L),f"{sc['id']}: {kk}={v} but scene has {len(L)} lines"
                        chk(v)
                elif isinstance(x,list):
                    for y in x: chk(y)
            chk(sc['els'])

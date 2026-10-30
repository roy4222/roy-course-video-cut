import os,sys,math;sys.path.insert(0,os.environ.get('EP_ENGINE','/workspace/video_style/epB_engine'))
from lib import Ep
ep=Ep(12,'模型準不準（下）：ROC、AUC 與門檻選擇','',
 '模型常常輸出的是機率，要用「門檻」才能變成有或沒有。這一集用保全系統的靈敏度打比方，看門檻一動，TPR 和 FPR 怎麼一起變；再用講義 20 筆資料一步步畫出 ROC 曲線、數格子算出 AUC＝0.68，最後比較 Youden 指數和最近點兩種挑門檻的方法。',
 ['機器學習','ROC','AUC','門檻','threshold','Youden','敏感度','特異度','機器學習從零開始','作業三'],'EP13 決策樹')
E=ep.E;L=ep.L
PROB=[.9,.8,.7,.6,.55,.54,.53,.52,.51,.5,.4,.39,.38,.37,.36,.35,.34,.33,.3,.1]
CLS='ppnpppnnpnpnpnnnpnpn'
ROC=[(0,0)];tp=fp=0
for c in CLS:
    if c=='p': tp+=1
    else: fp+=1
    ROC.append((fp/10,tp/10))
def gauss(mu,sd,xs): return [(x,math.exp(-(x-mu)**2/(2*sd*sd))) for x in xs]
XS=[i/50 for i in range(51)]
# ---------- title
ep.scene('title','',noHeader=True,chapter='開場',desc='EP12 標題卡＋今日地圖')
E('titlecard',ep='EP12 · 模型準不準（下）',title='ROC、AUC 與門檻選擇',sub='門檻一轉，四格就跟著變')
L('嗨，歡迎回到機器學習補習班。這是第十二集。')
L('上一集我們學了混淆矩陣和八個指標。今天要把它們變成一條曲線，看模型「整體」有多會分辨。')
i=L('今天的重點是三個字：門檻、ROC、AUC。我們一樣用講義的例子，一步一步手畫出來。')
E('text',s='今天的地圖',x=960,y=620,size=26,col='DIM',align='center',at=i)
E('chips',y=690,items=[dict(s='機率 → 門檻 → 類別',at=[i,0.3]),dict(s='TPR 與 FPR 的取捨',at=[i,0.6]),dict(s='手畫 ROC',at=[i,0.9]),dict(s='數格子算 AUC',at=[i,1.2]),dict(s='Youden・最近點',at=[i,1.5])],size=26)
# ---------- hook
ep.scene('hook','保全系統的靈敏度旋鈕',chapter='開場：保全系統的靈敏度',desc='一個靈敏度旋鈕：轉高 → 貓走過也響；轉低 → 小偷進來也不響',ref='PART03 p19')
a=L('想像你家裝了一套保全系統，上面有一個「靈敏度」的旋鈕。')
b=L('如果轉得很高，一點點動靜就響。小偷一定抓得到，可是半夜貓走過去，它也響，你被吵醒好幾次。')
c=L('如果轉得很低，它很安靜，不會亂響。可是小偷輕輕走進來，它也沒反應。')
d=L('你會發現，「抓到更多小偷」和「少一點誤報」，很難兩個同時都要。轉一個旋鈕，兩件事一起變。')
e=L('分類模型也有一個這樣的旋鈕，它叫「門檻」。今天就來看看，這個旋鈕要怎麼轉。')
E('card',x=150,y=220,w=520,h=500,title='靈敏度旋鈕',ts=34,col='A',at=a,align='center')
E('circle',x=410,y=480,r=120,col='A',at=a,lw=6)
E('arrow',x1=410,y1=480,x2=330,y2=390,col='BAD',at=b,until=c)
E('arrow',x1=410,y1=480,x2=490,y2=390,col='OK',at=c,until=d)
E('card',x=740,y=220,w=1030,h=230,title='轉高：很敏感',col='BAD',at=b,body=['小偷 → 一定抓到 ✓','貓走過 → 也會響 ✗（誤報變多）'],bs=30)
E('card',x=740,y=490,w=1030,h=230,title='轉低：很遲鈍',col='OK',at=c,body=['貓走過 → 不響 ✓','小偷 → 可能沒抓到 ✗（漏抓變多）'],bs=30)
E('chips',y=820,items=[dict(s='一個旋鈕，兩件事一起變',col='B',at=d),dict(s='模型的旋鈕 ＝ 門檻 threshold',col='A',at=e)],size=30)
# ---------- probability & threshold
ep.scene('prob','模型其實輸出的是「機率」',chapter='直覺：機率加上門檻才變成類別',desc='講義 p28 顧客流失例子：p̂＝0.72 與門檻 c＝0.5 比較 → 判成會流失',ref='PART03 p17、p28')
a=L('上一集的混淆矩陣，好像模型直接說「有」或「沒有」。但其實大部分的分類模型，先輸出的是一個機率。')
b=L('講義第二十八頁的例子：預測一位顧客會不會流失。模型算出來，他流失的機率是零點七二。')
c=L('可是零點七二不是答案，我們還要決定：機率多少以上，才算「會流失」？')
d=L('這條分界線，就叫「門檻」，也翻成「閾值」，英文是 threshold，講義寫成 c。')
e=L('如果門檻是零點五，零點七二大於零點五，就判成會流失，系統就可以寄優惠券挽留他。')
f=L('重點來了：門檻不同，分類結果就不同，混淆矩陣的四格也全部跟著變。所以只看「某一個門檻」的準確率，不能完整說明模型分辨的能力。')
E('flow',x=150,w=1620,y=250,items=[dict(s='模型輸出',sub='機率 p̂',col='A',at=a),dict(s='p̂ ＝ 0.72',sub='流失的機率',col='A',at=b),dict(s='和門檻 c 比',sub='p̂ ≥ c ？',col='B',at=d),dict(s='判成：會流失',sub='→ 寄優惠券',col='BAD',at=e)])
E('card',x=150,y=500,w=760,h=200,title='門檻 threshold（閾值）c',sub='機率多少以上，才算「有」？',col='B',at=d,body=['0.72 ≥ 0.5 → 會流失'],bs=30)
E('card',x=960,y=500,w=810,h=200,title='門檻一換，四格全部變',col='BAD',at=f,body=['只看一個門檻的 ACC 不夠'],bs=30)
# ---------- tradeoff
ep.scene('trade','門檻往左往右：TPR 與 FPR 一起變',chapter='敏感度與特異度的取捨',desc='兩座山：陰性（左）與陽性（右）分數分佈，門檻線左右移動，TPR、FPR 一起升降',ref='PART03 p18–21')
a=L('我們把所有資料的機率畫出來。左邊這座山是真的陰性的人，右邊這座山是真的陽性的人。兩座山中間有一段重疊。')
b=L('門檻是一條直線，線的右邊都判成陽性。先放在中間，零點五。')
c=L('把門檻往左移，變得很敏感：右邊的陽性幾乎全被抓到，TPR 變高；但左邊的陰性也有更多跑到線的右邊，FPR 也變高。')
d=L('把門檻往右移，變得很嚴格：誤報變少，FPR 變低；但很多陽性也被漏掉，TPR 也變低。')
e=L('這就是講義說的，敏感度和特異度的取捨，英文是 trade-off。TPR 和 FPR 是一起往上、一起往下的。')
f=L('那兩座山完全分開的模型呢？門檻放中間，就能全對，這是很會分辨的好模型；兩座山完全疊在一起，就怎麼切都分不好。')
E('plot',x=200,y=230,w=900,h=420,xr=[0,1],yr=[0,1.15],at=a,xlab='模型給的機率 p̂',ticks=dict(x=[0,0.5,1],y=[]),
  series=[dict(pts=gauss(.35,.12,XS),col='OK',lw=4,),dict(pts=gauss(.65,.12,XS),col='BAD',lw=4,),],
  marks=[dict(x=.35,y=1.08,r=0.1,col='OK',label='真的陰性 n',dx=0,dy=0,align='center',at=a),dict(x=.65,y=1.08,r=0.1,col='BAD',label='真的陽性 p',dx=0,dy=0,align='center',at=a)],
  vlines=[dict(x=.5,col='B',at=b,until=c),dict(x=.35,col='B',at=c,until=d),dict(x=.65,col='B',at=d,until=e)])
E('text',s='門檻線 c（線的右邊 → 判成陽性）',x=650,y=760,size=24,col='B',align='center',at=b)
E('card',x=1180,y=230,w=590,h=200,title='往左：很敏感',col='BAD',at=c,body=['TPR ↑（抓到更多）','FPR ↑（誤報也更多）'],bs=28)
E('card',x=1180,y=450,w=590,h=200,title='往右：很嚴格',col='OK',at=d,body=['FPR ↓（誤報變少）','TPR ↓（漏抓變多）'],bs=28)
E('chips',y=700,cx=1475,items=[dict(s='TPR、FPR 一起升降 ＝ trade-off',col='B',at=e)],size=26)
E('chips',y=840,items=[dict(s='兩山分開 ＝ 好模型',col='OK',at=f),dict(s='兩山重疊 ＝ 很難分',col='BAD',at=f)],size=26)
# ---------- ROC term
ep.scene('roc','名詞：ROC 曲線',chapter='名詞：ROC 曲線',desc='ROC 座標軸：x＝FPR、y＝TPR；四個角與對角線的意思',ref='PART03 p17、p21、p26')
a=L('既然每一個門檻都會得到一組 TPR 和 FPR，那我們乾脆把「所有」門檻都試一遍，全部畫在同一張圖上。')
b=L('這張圖的橫軸是 FPR，偽陽性率；縱軸是 TPR，也就是召回率。每一個門檻，就是圖上的一個點。')
c=L('把這些點連起來，就是 ROC 曲線。ROC 是 Receiver Operating Characteristic 的縮寫，中文叫「接收者操作特徵曲線」。名字是二戰雷達留下來的，不用背，記住「x 是 FPR、y 是 TPR」就好。')
d=L('看四個位置。門檻設成超高，什麼都說沒有，TPR 和 FPR 都是零，在左下角。')
e=L('門檻設成超低，什麼都說有，TPR 和 FPR 都是一，在右上角。')
f=L('左上角是 TPR 等於一、FPR 等於零，全部抓到又完全沒誤報，是完美模型的位置。')
g=L('對角線則是「亂猜」的模型。所以曲線越往左上角拱，模型越好；貼著對角線，就跟丟銅板差不多。')
E('plot',x=260,y=220,w=520,h=520,xr=[0,1],yr=[0,1],at=b,xlab='FPR（偽陽性率）',ylab='TPR（召回率）',ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),diag=True,
  series=[dict(pts=[(0,0),(.05,.45),(.15,.7),(.3,.85),(.55,.95),(1,1)],col='A',at=c,draw=3)],
  marks=[dict(x=0,y=0,col='DIM',at=d,label='全說沒有',dx=16,dy=-24),dict(x=1,y=1,col='DIM',at=e,label='全說有',dx=-14,dy=30,align='right'),dict(x=0,y=1,col='OK',at=f,label='完美',dx=16,dy=26)])
E('formula',x=950,y=220,w=820,h=180,lines=[dict(s='x 軸 ＝ FPR',at=b,col='BAD'),dict(s='y 軸 ＝ TPR ＝ Recall',at=b,col='B')],size=34)
E('card',x=950,y=430,w=820,h=170,title='ROC 曲線',sub='Receiver Operating Characteristic',col='A',at=c,body=['每個門檻 → 一個點 → 連成線'],bs=26)
E('card',x=950,y=630,w=820,h=130,title='越往左上拱越好；貼著對角線 ＝ 亂猜',ts=30,col='OK',at=g)
# ---------- worked example 1
def tables(at,fills=None,until=None,**kw):
    rows=[[str(i+1),CLS[i],f'{PROB[i]:.2f}'] for i in range(20)]
    for half in (0,1):
        fl=[dict(f,row=f['row']-half*10) for f in (fills or []) if half*10<=f['row']<half*10+10]
        E('table',x=150+half*330,y=200,ws=[70,90,140],head=['#','類別','機率'],rows=rows[half*10:half*10+10],rh=52,hh=52,fs=24,at=at,until=until,
          cellCol=[dict(row=r,col=1,c='BAD' if rows[half*10+r][1]=='p' else 'OK',at=at) for r in range(10)],fills=fl,**kw)
ep.scene('ex1','手算例題（一）：門檻 0.6 的一個點',chapter='手算例題：門檻 0.6 得到一個點',desc='講義 p22／p24 的 20 筆資料（10 p、10 n），門檻 0.6：TP 3、FP 1 → 點 (0.1, 0.3)',ref='PART03 p22、p24')
a=L('好，來手畫一條 ROC。講義第二十二頁有二十筆資料，十筆真的是陽性 p，十筆真的是陰性 n，已經照模型給的機率，由大排到小。')
b=L('先試一個門檻：零點六。機率大於等於零點六的，判成陽性，就是前四筆。')
c=L('這四筆裡面，第一、二、四筆真的是 p，所以 TP 是三；第三筆其實是 n，所以 FP 是一。')
d=L('TPR 就是 TP 除以全部的陽性十筆，三除以十，零點三。FPR 是 FP 除以全部的陰性十筆，一除以十，零點一。')
e=L('所以門檻零點六，在 ROC 圖上就是一個點：FPR 零點一、TPR 零點三。跟講義第二十四頁的答案一樣。')
tables(a,fills=[dict(row=r,col='B',at=b) for r in range(4)])
E('formula',x=850,y=200,w=920,h=250,lines=[dict(s='門檻 c ＝ 0.6 → 前 4 筆判成 p',at=b,cjk=True,w=700),dict(s='TP = 3（#1, #2, #4）  FP = 1（#3）',at=c),dict(s='TPR = 3/10 = 0.3   FPR = 1/10 = 0.1',at=d,col='B')],size=30)
E('plot',x=1060,y=500,w=330,h=290,xr=[0,1],yr=[0,1],at=e,ticks=dict(x=[0,1],y=[0,1]),diag=True,series=[],marks=[dict(x=.1,y=.3,col='B',at=e,label='(0.1, 0.3)',dx=16,dy=-16,mono=True)])
# ---------- worked example 2
ep.scene('ex2','手算例題（二）：門檻一路往下，畫出整條曲線',chapter='手算例題：一步步畫出整條 ROC',desc='門檻從最高往下一筆一筆移：遇到 p 往上 0.1，遇到 n 往右 0.1，連成階梯狀 ROC',ref='PART03 p22–24')
a=L('如果每個門檻都這樣算一次，二十個門檻要算二十次，太累了。其實有個超簡單的走法。')
b=L('從左下角零零出發。把門檻從最高往下，一次多放進一筆。')
c=L('多放進來的如果是 p，TP 多一，TPR 加零點一，點就往「上」走一格。')
d=L('如果是 n，FP 多一，FPR 加零點一，點就往「右」走一格。')
e=L('我們走走看：第一筆 p，往上；第二筆 p，往上；第三筆 n，往右；第四筆 p，往上。這就走到剛剛的零點一、零點三。')
f=L('接著第五、第六筆是 p，往上兩格；第七、第八筆是 n，往右兩格……一路走到最後一筆，終點一定是右上角，一點一。')
g=L('走完就是一條階梯狀的 ROC 曲線，跟講義第二十三頁的圖一模一樣。')
tables(a)
E('card',x=820,y=200,w=400,h=220,title='走法',col='A',at=b,body=[dict(s='遇到 p → 往上 0.1',at=c,col='BAD'),dict(s='遇到 n → 往右 0.1',at=d,col='OK'),dict(s='起點 (0,0)・終點 (1,1)',at=f)],bs=28)
E('plot',x=1330,y=210,w=430,h=430,xr=[0,1],yr=[0,1],at=b,ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),diag=True,xlab='FPR',ylab='TPR',
  series=[dict(pts=ROC[:5],col='B',at=e,draw=4,dots=6),dict(pts=ROC[4:],col='B',at=f,draw=8,dots=6)],
  marks=[dict(x=.1,y=.3,col='A',at=[e,4],label='c＝0.6',dx=14,dy=-4,size=20)])
E('chips',y=740,cx=1060,items=[dict(s='p p n p p p n n p n …',col='DIM',at=e)],size=26)
E('chips',y=820,cx=1060,items=[dict(s='階梯狀 ROC ＝ 講義 p23',col='OK',at=g)],size=28)
# ---------- AUC
ep.scene('auc','名詞：AUC，曲線下的面積',chapter='名詞：AUC 與數格子手算',desc='ROC 下方面積塗色；10×10 小格，每欄高度相加 6.8 → AUC＝0.68',ref='PART03 p25–26')
a=L('一條曲線很難直接比大小，所以我們把它變成一個數字：曲線下面的面積。')
b=L('它叫做 AUC，Area Under the ROC Curve，中文就是「ROC 曲線下的面積」。整張圖是一乘一，所以 AUC 介於零到一之間。')
c=L('來手算。圖被切成十乘十，一百個小格子，每格面積是零點零一。我們只要數曲線下面有幾格。')
d=L('一欄一欄數。每一欄的高度，就是遇到那個 n 的時候，曲線已經爬到多高。')
e=L('十個 n 出現時的高度依序是：二、五、五、六、七、八、八、八、九、十格。')
f=L('加起來是六十八格，乘上零點零一，AUC 就是零點六八。')
g=L('怎麼解讀？AUC 等於一是完美；零點五就是對角線，跟亂猜一樣。零點六八代表：隨便抽一個 p、一個 n，模型給 p 比較高分的機率是百分之六十八。')
E('plot',x=200,y=220,w=520,h=520,xr=[0,1],yr=[0,1],at=a,ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),diag=True,grid=10,xlab='FPR',ylab='TPR',
  series=[dict(pts=ROC,col='B')],fillUnder=[dict(si=0,col='B',at=b)])
E('formula',x=850,y=220,w=920,h=240,lines=[dict(s='AUC = Area Under the ROC Curve',at=b,col='B'),dict(s='0 ≤ AUC ≤ 1・每小格 ＝ 0.1 × 0.1 ＝ 0.01',at=c,cjk=True,w=700)],size=30)
E('formula',x=850,y=490,w=920,h=180,lines=[dict(s='高度：2+5+5+6+7+8+8+8+9+10 = 68 格',at=e,cjk=True,w=700),dict(s='AUC = 68 × 0.01 = 0.68',at=f,col='OK')],size=30)
E('chips',y=730,cx=1310,items=[dict(s='1 ＝ 完美',col='OK',at=g),dict(s='0.5 ＝ 亂猜',col='BAD',at=g),dict(s='0.68：p 比 n 高分的機率',col='B',at=g)],size=24)
# ---------- compare
ep.scene('cmp','用 ROC 和 AUC 比較模型',chapter='用 ROC、AUC 比較模型',desc='三條 ROC：完美（AUC 1）、普通、亂猜（0.5）；單一門檻的 ACC 可能誤導',ref='PART03 p26–27')
a=L('講義第二十六頁，把幾種模型的 ROC 放在一起比較。')
b=L('兩座山完全分開的模型，ROC 直接衝到左上角，AUC 是一。')
c=L('兩座山有點重疊，曲線拱起來但沒那麼高，AUC 大概零點七到零點九。')
d=L('兩座山完全疊在一起，曲線就是對角線，AUC 零點五。')
e=L('講義第二十七頁還提醒一個陷阱：兩個模型在「某一個門檻」的準確率可能一樣，但 AUC 差很多。所以比較模型時，看整條曲線比只看一個點可靠。')
E('plot',x=200,y=220,w=520,h=520,xr=[0,1],yr=[0,1],at=a,ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),xlab='FPR',ylab='TPR',
  series=[dict(pts=[(0,0),(0,1),(1,1)],col='OK',at=b,draw=1.5,lw=5),dict(pts=[(0,0),(.05,.45),(.15,.7),(.3,.85),(.55,.95),(1,1)],col='B',at=c,draw=2),dict(pts=[(0,0),(1,1)],col='BAD',at=d,draw=1.5,dash=[10,8])])
E('bullets',x=850,y=230,w=920,size=30,gap=16,items=[dict(s='兩山分開 → 衝到左上角 → AUC ＝ 1',at=b,col='OK'),dict(s='有點重疊 → 拱起來 → AUC 約 0.7～0.9',at=c,col='B'),dict(s='完全重疊 → 對角線 → AUC ＝ 0.5',at=d,col='BAD')])
E('card',x=850,y=600,w=920,h=150,title='陷阱：同一門檻 ACC 一樣，AUC 卻可能差很多',ts=30,col='A',at=e,body=['→ 比較模型看整條曲線'],bs=26)
# ---------- is 0.5 best
ep.scene('half','門檻一定要用 0.5 嗎？',chapter='補充：0.5 一定最好嗎？',desc='講義 p30–32：0.5 只是預設；最佳門檻取決於類別比例、錯誤成本、資源與目標；三種常見方法',ref='PART03 p29–32',tag='補充',tagCol='PUR')
a=L('接下來是講義的補充：門檻一定要用零點五嗎？')
b=L('零點五只是大家習慣的預設值，不一定是最好的。而且有些模型輸出的不是真正的機率，只是一個分數，這時候零點五根本沒有意義。')
c=L('講義說，最好的門檻，要看四件事：類別的比例、兩種錯誤的成本、手上有多少資源，還有你的決策目標。')
d=L('例如顧客流失：如果行銷預算只夠聯絡一百位顧客，門檻就要設在「剛好選出最可能流失的一百位」。')
e=L('講義列了三種常見的方法：Youden 指數、離左上角最近的點，還有以成本為基礎的門檻。我們一個一個看。')
E('card',x=150,y=220,w=760,h=240,title='0.5 只是預設值',col='B',at=a,body=[dict(s='不一定最好',at=b),dict(s='輸出是分數不是機率時 → 0.5 沒意義',at=b)],bs=28)
E('bullets',x=980,y=220,w=790,size=28,gap=12,items=[dict(s='類別比例 class distribution',at=c),dict(s='錯誤成本 error costs',at=c),dict(s='可用資源 resources',at=[c,1]),dict(s='決策目標 objective',at=[c,1])])
E('card',x=150,y=500,w=760,h=170,title='例：預算只夠聯絡 100 位顧客',ts=30,col='A',at=d,body=['→ 門檻設在剛好選出前 100 位'],bs=26)
E('chips',y=790,items=[dict(s='① Youden 指數',col='OK',at=[e,0.5]),dict(s='② 最近左上角',col='B',at=[e,1.5]),dict(s='③ 成本為基礎',col='PUR',at=[e,2.5])],size=30)
# ---------- youden
ep.scene('youden',"方法一：Youden 指數",chapter="方法一：Youden 指數",desc='J＝TPR−FPR；在 20 筆資料上逐一計算，門檻 0.54 時 J 最大＝0.4',ref='PART03 p31–34')
a=L('第一種，Youden 指數，寫成 J。')
b=L('公式是敏感度加特異度減一，因為特異度等於一減 FPR，所以也等於 TPR 減 FPR。')
c=L('白話是：「抓到的比例」減掉「誤報的比例」，越大越好。它把敏感度和特異度看得一樣重要。')
d=L('在圖上，J 就是那個點，到對角線的垂直高度。我們要找最高的那個點。')
e=L('用我們的二十筆資料來算。門檻零點六，TPR 零點三、FPR 零點一，J 是零點二。')
f=L('門檻零點五四，TPR 零點五、FPR 零點一，J 是零點四。門檻零點五，TPR 零點六、FPR 零點四，J 只有零點二。')
g=L('把每個門檻都算完，最大的 J 是零點四，在門檻零點五四。注意，它不是零點五。')
E('formula',x=150,y=210,w=820,h=260,lines=[dict(s='J = Sensitivity + Specificity − 1',at=b),dict(s='  = TPR − FPR',at=[b,2],col='OK'),dict(s='抓到的比例 − 誤報的比例',at=c,cjk=True,w=700,col='DIM')],size=32)
E('table',x=150,y=510,w=820,ws=[200,200,200,220],head=['門檻 c','TPR','FPR','J'],rows=[['0.60','0.3','0.1','0.2'],['0.54','0.5','0.1','0.4'],['0.50','0.6','0.4','0.2']],rh=60,hh=56,fs=28,at=e,rowAt=[e,f,[f,3]],
  fills=[dict(row=1,col='OK',at=g)])
E('plot',x=1150,y=220,w=560,h=560,xr=[0,1],yr=[0,1],at=d,ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),diag=True,xlab='FPR',ylab='TPR',
  series=[dict(pts=ROC,col='B')],segs=[dict(pts=[(.1,.1),(.1,.5)],col='OK',at=g)],
  marks=[dict(x=.1,y=.3,col='DIM',at=e,label='0.6',dx=14,dy=10,size=20),dict(x=.1,y=.5,col='OK',at=f,label='0.54：J＝0.4',dx=14,dy=-10,size=22),dict(x=.4,y=.6,col='DIM',at=[f,3],label='0.5',dx=14,dy=14,size=20)])
E('chips',y=860,items=[dict(s='最大 J ＝ 0.4 在門檻 0.54，不是 0.5',col='OK',at=g)],size=28)
# ---------- closest
ep.scene('closest','方法二：離左上角最近的點',chapter='方法二：最近左上角的點',desc='d＝√(FPR²＋(1−TPR)²)；在 20 筆資料上 d 最小＝0.5，出現在門檻 0.51 與 0.40，和 Youden 不同',ref='PART03 p31–35')
a=L('第二種方法：既然左上角是完美的位置，那就挑離左上角最近的點。')
b=L('距離用畢氏定理算：d 等於根號，FPR 的平方，加上一減 TPR 的平方。d 越小越好。')
c=L('門檻零點五四那個點：FPR 零點一，一減 TPR 是零點五。零點一的平方加零點五的平方，是零點二六，開根號約零點五一。')
d=L('門檻零點五一：FPR 零點三、TPR 零點六。零點三的平方加零點四的平方，是零點二五，開根號剛好零點五。')
e=L('門檻零點四：FPR 零點四、TPR 零點七，零點四平方加零點三平方，也是零點二五，也是零點五。兩個並列最近。')
f=L('所以在同一份資料上，Youden 選零點五四，最近點選零點五一或零點四。講義第三十三到三十五頁就在說這件事：兩種方法都想往左上角靠，但量距離的方式不同，不一定選出同一個門檻。')
E('formula',x=150,y=210,w=900,h=170,lines=[dict(s='d = √( FPR² + (1 − TPR)² )',at=b,col='B'),dict(s='d 越小越好',at=b,cjk=True,w=700,col='DIM')],size=34)
E('table',x=150,y=420,ws=[160,140,140,220,200],head=['門檻 c','FPR','TPR','FPR²＋(1−TPR)²','d'],rows=[['0.54','0.1','0.5','0.01 + 0.25','≈ 0.51'],['0.51','0.3','0.6','0.09 + 0.16','0.50'],['0.40','0.4','0.7','0.16 + 0.09','0.50']],rh=62,hh=56,fs=26,at=c,rowAt=[c,d,e],
  fills=[dict(row=1,col='B',at=f),dict(row=2,col='B',at=f)])
E('plot',x=1150,y=220,w=560,h=560,xr=[0,1],yr=[0,1],at=a,ticks=dict(x=[0,0.5,1],y=[0,0.5,1]),diag=True,xlab='FPR',ylab='TPR',
  series=[dict(pts=ROC,col='DIM')],segs=[dict(pts=[(0,1),(.1,.5)],col='DIM',dash=[6,6],at=c,lw=3),dict(pts=[(0,1),(.3,.6)],col='B',at=d,lw=3),dict(pts=[(0,1),(.4,.7)],col='B',at=e,lw=3)],
  marks=[dict(x=0,y=1,col='OK',at=a,label='(0,1)',dx=14,dy=24,size=20),dict(x=.1,y=.5,col='OK',at=c,label='Youden 0.54',dx=14,dy=10,size=20),dict(x=.3,y=.6,col='B',at=d,label='0.51',dx=14,dy=16,size=20),dict(x=.4,y=.7,col='B',at=e,label='0.40',dx=14,dy=16,size=20)])
E('card',x=150,y=690,w=900,h=110,title='同一份資料：Youden → 0.54；最近點 → 0.51 或 0.40',ts=28,col='A',at=f)
# ---------- which method
ep.scene('which','三種方法，什麼時候用哪個？',chapter='方法三：成本，以及怎麼選',desc='講義 p35–36：Youden（敏感度、特異度一樣重要）、最近點（偏好兩者平衡）、成本法（知道錯誤代價時）',ref='PART03 p33–36')
a=L('最後一種，是以成本為基礎的門檻：如果你知道漏抓一個要賠多少錢、誤報一個要花多少錢，就選讓總成本最低、或利潤最高的門檻。')
b=L('那三種方法怎麼挑？Youden 指數，適合你覺得敏感度和特異度一樣重要的時候。')
c=L('最近點因為用平方，會特別懲罰「某一邊特別差」的點，所以偏好兩邊比較平衡的門檻。')
d=L('如果真的知道兩種錯誤的代價，例如顧客流失、醫療篩檢，就用成本法，這最貼近真實的決策。')
e=L('講義的結論：最佳門檻，最後還是要由研究者，依照決策目標來定義。寫作業三的時候，可以用 AUC 比模型，再說明你的門檻怎麼選。')
E('card',x=150,y=220,w=520,h=330,title='① Youden 指數',sub='max (TPR − FPR)',col='OK',at=b,body=['敏感度、特異度','一樣重要'],bs=28)
E('card',x=700,y=220,w=520,h=330,title='② 最近左上角',sub='min √(FPR² + FNR²)',col='B',at=c,body=['平方 → 重罰偏一邊','偏好兩邊平衡'],bs=28)
E('card',x=1250,y=220,w=520,h=330,title='③ 成本法',sub='min 總成本／max 利潤',col='PUR',at=a,body=[dict(s='知道兩種錯的代價時',at=d),dict(s='最貼近真實決策',at=d)],bs=28)
E('card',x=150,y=610,w=1620,h=150,title='最佳門檻 ＝ 依決策目標定義・作業三可用 AUC 比模型',ts=32,col='A',align='center',at=e)
# ---------- mistakes
ep.scene('mistakes','常見誤區',chapter='常見誤區',desc='五張紅色警示卡',ref='PART03 p17–36')
a=L('整理幾個常見的錯誤。')
b=L('第一，座標軸放反。ROC 的橫軸是 FPR，縱軸是 TPR。')
c=L('第二，TPR 和 FPR 的分母搞錯。TPR 除以全部真的陽性，FPR 除以全部真的陰性，不是除以全部資料。')
d=L('第三，以為 AUC 是某一個門檻的準確率。AUC 是看「所有」門檻，跟門檻無關。')
e=L('第四，門檻預設零點五就不管了。要說明為什麼選這個門檻。')
f=L('第五，以為 Youden 和最近點一定選出同一個門檻。今天的例子就不一樣。')
E('bullets',x=150,y=210,w=1620,size=30,gap=14,items=[dict(s='ROC：橫軸 FPR、縱軸 TPR，別放反',at=b,col='BAD'),dict(s='TPR ÷ 真的陽性 P；FPR ÷ 真的陰性 N（不是 ÷ 全部）',at=c,col='BAD'),dict(s='AUC 看所有門檻，不是某個門檻的 ACC',at=d,col='BAD'),dict(s='門檻不一定是 0.5，要說明怎麼選',at=e,col='BAD'),dict(s='Youden 與最近點不一定選同一個門檻',at=f,col='BAD')])
# ---------- quiz
ep.scene('quiz','小測驗',chapter='小測驗',desc='三題，倒數暫停後揭曉')
L('來個小測驗，可以先暫停想一想。')
q1=L('第一題：把門檻往下調，TPR 和 FPR 會怎麼變？',gap=3.0)
a1=L('兩個都會變大，或至少不會變小。說有的變多，抓到的和誤報的都會增加。')
q2=L('第二題：某個模型的 AUC 是零點五，代表什麼？',gap=3.0)
a2=L('代表它跟亂猜差不多，ROC 曲線貼著對角線。')
q3=L('第三題：一個點 TPR 零點八、FPR 零點三，Youden 的 J 是多少？',gap=3.0)
a3=L('J 等於 TPR 減 FPR，零點八減零點三，等於零點五。')
E('quiz',y=215,qs=[dict(q='Q1　門檻往下調，TPR、FPR 怎麼變？',a='兩個都變大（說有的變多）',qi=q1,ai=a1),dict(q='Q2　AUC ＝ 0.5 代表？',a='跟亂猜一樣（貼著對角線）',qi=q2,ai=a2),dict(q='Q3　TPR 0.8、FPR 0.3，J ＝ ？',a='J ＝ 0.8 − 0.3 ＝ 0.5',qi=q3,ai=a3)])
# ---------- recap
ep.scene('recap','重點回顧',chapter='重點回顧與下集預告',desc='回顧＋下集預告卡')
a=L('今天的重點整理一下。')
b=L('模型先輸出機率，再用門檻切成有或沒有。門檻一動，TPR 和 FPR 一起變。')
c=L('把所有門檻的點畫出來，橫軸 FPR、縱軸 TPR，就是 ROC 曲線；越往左上越好。')
d=L('曲線下的面積叫 AUC，一是完美，零點五是亂猜。我們手算的例子是零點六八。')
e=L('門檻不一定是零點五：可以用 Youden 指數、最近點，或成本來選。')
f=L('模型評估的工具準備好了。下一集，我們正式進入第一個模型：決策樹。我們會用玩「猜猜我是誰」的方式，認識它。我們下集見！')
E('bullets',x=160,y=210,w=1600,size=30,gap=12,items=[dict(s='機率 ＋ 門檻 → 類別；門檻一動，TPR・FPR 一起變',at=b),dict(s='ROC：x ＝ FPR、y ＝ TPR；越往左上越好',at=c),dict(s='AUC ＝ 曲線下面積；1 完美、0.5 亂猜；例題 0.68',at=d),dict(s='選門檻：Youden（max TPR − FPR）、最近點、成本法',at=e)])
E('card',x=160,y=720,w=1600,h=110,title='下一集 EP13：決策樹是什麼？像玩「猜猜我是誰」',ts=34,col='A',align='center',at=f,fill='#11161d')
ep.save('.')

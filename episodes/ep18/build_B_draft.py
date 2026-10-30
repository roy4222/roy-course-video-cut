import os,sys,json;sys.path.insert(0,os.environ.get('EP_ENGINE','/workspace/video_style/epB_engine'))
def _wx(*parts):
    base=os.environ.get('WORKED_EXAMPLES') or os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','_worked_examples'))
    p=os.path.join(base,*parts)
    return p if os.path.exists(p) else os.path.join('/workspace/video_style',*parts)
from lib import Ep
CV=json.load(open(_wx('epB_src','ep18_cv.json')))
P=lambda v:f'{v*100:.1f}%'
ep=Ep(18,'交叉驗證：Holdout、K-fold、Nested CV','',
 '只切一次驗證集，結果可能看運氣。這一集用「模擬考輪流當考官」打比方，介紹 Holdout、K-fold、重複與分層 CV，實際用 3-fold CV 比較 max_depth＝2、5、20，再說明為什麼要用 Nested CV、Public／Private test，以及交叉驗證下怎麼畫 ROC，最後把作業三指定的兩種流程畫清楚。',
 ['機器學習','交叉驗證','cross-validation','K-fold','Holdout','Nested CV','超參數','機器學習從零開始','作業三'],'EP19 剪枝')
E=ep.E;L=ep.L
# ---------- title
ep.scene('title','',noHeader=True,chapter='開場',desc='EP18 標題卡＋今日地圖')
E('titlecard',ep='EP18 · 模型評估（二）',title='交叉驗證',sub='讓每一筆資料都輪流當一次考官')
L('嗨，歡迎回到機器學習補習班。這是第十八集。')
L('上一集我們說，要用驗證集來挑超參數。今天要問：驗證集到底要怎麼切，結果才可靠？')
i=L('這一集會直接對到作業三規定的兩種流程，看完你就知道資料要怎麼切、要重複幾次。')
E('text',s='今天的地圖',x=960,y=620,size=26,col='DIM',align='center',at=i)
E('chips',y=690,items=[dict(s='選擇偏誤',at=[i,0.3]),dict(s='Holdout',at=[i,0.6]),dict(s='K-fold',at=[i,0.9]),dict(s='用 CV 選超參數',at=[i,1.2]),dict(s='Nested CV',at=[i,1.5]),dict(s='作業三流程',at=[i,1.8],col='B')],size=26)
# ---------- hook
ep.scene('hook','只考一次模擬考，準嗎？',chapter='開場：一次模擬考準嗎？',desc='三次模擬考成績差很多；只看一次可能剛好考到會的題目',ref='PART03 p170–171')
a=L('想像你要估計自己的實力，只考了一次模擬考，八十五分。這個分數準嗎？')
b=L('不一定。可能剛好考到你最熟的章節。換一份卷子，也許只剩七十分。')
c=L('比較可靠的方法，是多考幾次不同的卷子，再看平均。如果三次是八十五、七十、七十六，平均大約七十七，這才比較接近真正的實力。')
d=L('評估模型也是一樣。只切一次驗證集，分數可能看運氣。今天要學的「交叉驗證」，就是讓模型多考幾次、每次換一份考卷。')
E('bars',x=200,y=260,w=700,h=420,at=a,max=100,items=[dict(label='第 1 次',v=85,col='A',at=a),dict(label='第 2 次',v=70,col='A',at=b),dict(label='第 3 次',v=76,col='A',at=c)])
E('card',x=1000,y=230,w=770,h=180,title='只考一次：85 分',sub='可能剛好考到最熟的章節',col='BAD',at=a)
E('card',x=1000,y=440,w=770,h=180,title='考三次平均 ≈ 77 分',sub='(85 + 70 + 76) / 3 ≈ 77',col='OK',at=c)
E('card',x=1000,y=650,w=770,h=130,title='交叉驗證 ＝ 多考幾次、每次換卷子',ts=30,col='B',at=d)
# ---------- selection bias
ep.scene('bias','驗證誤差也會「太樂觀」',chapter='驗證誤差與選擇偏誤',desc='講義 p169：同一份驗證集反覆用來挑模型 → 模型慢慢適應驗證集 → 驗證誤差低估泛化誤差',ref='PART03 p169')
a=L('先講一個容易被忽略的問題。挑模型和超參數的時候，我們會反覆使用同一份驗證資料。')
b=L('試了一百種設定，每次都看驗證成績，挑最高的那個。久而久之，選出來的模型，就會慢慢「適應」這份驗證資料。')
c=L('就像同一份模擬考，你考了十次，最後一次一定考很高。但那是因為你記住了這份卷子，不是實力真的變強。')
d=L('所以講義說：驗證誤差可能會低估真正的泛化誤差，這叫「選擇偏誤」，selection bias。驗證成績，不能直接當成最後的成績來報告。')
E('flow',x=150,w=1620,y=230,items=[dict(s='試很多設定',sub='每次都看驗證成績',col='A',at=a),dict(s='挑最高的',sub='反覆使用同一份',col='B',at=b),dict(s='模型適應驗證集',sub='越挑越像它',col='BAD',at=[b,3])],h=120)
E('card',x=150,y=430,w=780,h=200,title='同一份模擬考考十次',col='PUR',at=c,body=['最後一次很高 ≠ 實力變強'],bs=28)
E('card',x=990,y=430,w=780,h=200,title='選擇偏誤 selection bias',col='BAD',at=d,body=['驗證誤差 → 低估泛化誤差','不能當最後成績報告'],bs=28)
# ---------- holdout
ep.scene('holdout','方法一：Holdout 保留法',chapter='Holdout 保留法與重複 Holdout',desc='講義 p170：隨機切成兩份互不重疊；訓練多 → 學得好，測試多 → 評估穩；重複 Holdout 降低運氣成分',ref='PART03 p170')
a=L('最簡單的方法叫 Holdout，中文叫保留法：把資料隨機切成兩份，互不重疊。一份拿來訓練，另一份「保留」起來，拿來評估。')
b=L('切的比例是個取捨。訓練的部分多一點，模型學得比較好；評估的部分多一點，分數比較可靠。常見的是八比二。')
c=L('缺點是：只切一次，結果就看這一刀切得好不好，有運氣成分。')
d=L('改良的方法是「重複 Holdout」：用不同的隨機種子，切好幾次，每次都算一個分數，最後取平均。隨機種子，就是決定「怎麼亂切」的一個號碼，號碼一樣，切法就一樣，可以重現。')
E('blocks',x=200,y=240,bw=144,bh=90,gap=8,fs=28,at=a,rows=[dict(cells=[dict(s='訓練 80%',span=8,col='A'),dict(s='保留 20%',span=2,col='B')])])
E('blocks',x=200,y=420,bw=144,bh=60,gap=8,fs=22,at=d,rows=[dict(label='種子 1',cells=[dict(s='訓練',span=8),dict(s='評估',span=2,col='B')]),dict(label='種子 2',cells=[dict(s='訓練',span=3),dict(s='評估',span=2,col='B'),dict(s='訓練',span=5)]),dict(label='種子 3',cells=[dict(s='評估',span=2,col='B'),dict(s='訓練',span=8)])],rgap=16)
E('chips',y=380,items=[dict(s='訓練多 → 學得好',col='A',at=b),dict(s='評估多 → 分數穩',col='B',at=b),dict(s='只切一次 → 看運氣',col='BAD',at=c)],size=26)
E('chips',y=720,items=[dict(s='重複 Holdout：換種子切幾次 → 取平均',col='OK',at=d),dict(s='種子一樣 → 切法一樣（可重現）',col='DIM',at=[d,3])],size=26)

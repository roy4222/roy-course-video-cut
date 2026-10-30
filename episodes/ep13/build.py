import os,sys;sys.path.insert(0,os.environ.get('EP_ENGINE','/workspace/video_style/epB_engine'))
from lib import Ep
ep=Ep(13,'決策樹是什麼？像玩「猜猜我是誰」','',
 '決策樹就是用一連串「是非題」來做判斷的模型。這一集用「猜猜我是誰」和客服語音選單打比方，認識根節點、內部節點、葉節點和測試條件，再用講義的貸款資料，把一位新客戶從樹根一路走到葉子，判斷他會不會違約。',
 ['機器學習','決策樹','decision tree','根節點','葉節點','分類','機器學習從零開始','Hunt演算法前置'],'EP14 Hunt\'s 演算法')
E=ep.E;L=ep.L
# ---------- title
ep.scene('title','',noHeader=True,chapter='開場',desc='EP13 標題卡＋今日地圖')
E('titlecard',ep='EP13 · 決策樹（一）',title='決策樹是什麼？',sub='像玩「猜猜我是誰」一樣做判斷')
L('嗨，歡迎回到機器學習補習班。這是第十三集。')
L('從這一集開始，我們要認識這門課的第一個正式模型：決策樹。')
i=L('今天不會有難的數學，我們只要學會「看懂一棵樹」，還有「沿著樹走一遍」。')
E('text',s='今天的地圖',x=960,y=620,size=26,col='DIM',align='center',at=i)
E('chips',y=690,items=[dict(s='用是非題做決定',at=[i,0.3]),dict(s='三種節點',at=[i,0.6]),dict(s='測試條件',at=[i,0.9]),dict(s='新資料走到葉子',at=[i,1.2]),dict(s='一份資料・很多棵樹',at=[i,1.5])],size=28)
# ---------- hook
ep.scene('hook','先玩個遊戲：猜猜我是誰',chapter='開場遊戲：猜猜我是誰',desc='左邊一串是非題，右邊候選動物一隻隻被刪掉，最後剩下答案',ref='PART03 p38')
a=L('先來玩個小遊戲。我心裡想好一種動物，你只能問我「是」或「不是」的問題。')
b=L('你可能會先問：牠是哺乳類嗎？我說：是。')
c=L('再問：牠會飛嗎？我說：不會。')
d=L('再問：牠住在水裡嗎？我說：是。')
e=L('這時候你大概就猜得出來了：是鯨魚，或是海豚。')
f=L('你有沒有發現，每問一個問題，候選答案就少掉一大半？')
g=L('這種「一題接一題問下去，最後得到答案」的思考方式，就是今天的主角：決策樹。')
for k,(q,ans,at) in enumerate([('是哺乳類嗎？','是',b),('會飛嗎？','不是',c),('住在水裡嗎？','是',d)]):
    E('card',x=150,y=220+k*150,w=620,h=120,title=f'Q{k+1}　{q}',ts=36,col='A',at=at)
    E('text',s=ans,x=700,y=280+k*150,size=34,col='OK' if ans=='是' else 'BAD',w=700,align='center',at=[at,1.2])
an=['老鷹','鴿子','蝙蝠','狗','貓','鯊魚','鯨魚','海豚','青蛙','蛇']
gone={'老鷹':b,'鴿子':b,'鯊魚':b,'青蛙':b,'蛇':b,'蝙蝠':c,'狗':d,'貓':d}
E('card',x=880,y=220,w=890,h=420,title='候選答案',ts=30,col='LINE',at=a)
for k,n in enumerate(an):
    x=1010+(k%5)*165;y=360+(k//5)*130
    E('text',s=n,x=x,y=y,size=36,col='INK',w=700,align='center',at=a,until=gone.get(n) if n in gone else None)
    if n in gone: E('cross',x=x,y=y,s=60,at=[gone[n],1.5],until=[gone[n],3.2])
E('hl',x=1080,y=440,w=360,h=100,col='OK',at=e)
E('card',x=880,y=680,w=890,h=110,title='每問一題，候選就少掉一大半',ts=34,col='B',align='center',at=f)
E('chips',y=860,items=[dict(s='一題接一題 → 得到答案 ＝ 決策樹',col='A',at=g)],size=30)
# ---------- intuition
ep.scene('intuition','生活裡的決策樹：客服語音選單',chapter='直覺：客服語音選單',desc='客服電話語音選單畫成樹狀圖，一路按鍵走到「轉接專人」',ref='PART03 p38–41')
a=L('其實你每天都在用決策樹，只是沒發現。')
b=L('打電話給電信公司客服，會聽到：中文請按一，English press two。')
c=L('按了一以後，又問：查帳單請按一，手機故障請按二。')
d=L('你再按二，它又問：螢幕壞了請按一，不能開機請按二。')
e=L('每一次按鍵，都是在回答一個問題；回答完，就往下一層走。')
f=L('走到最底下，就得到一個結果，例如「幫你轉接維修專員」。')
g=L('把這些問題畫出來，就像一棵倒過來的樹：最上面只有一個開頭，越往下分岔越多。')
E('tree',at=a,nodes=[dict(id='r',x=960,y=270,label='語言？',at=b),dict(id='en',x=1450,y=430,label='English menu',leaf=True,at=[b,1]),
 dict(id='zh',x=600,y=430,label='要辦什麼？',at=c),dict(id='bill',x=300,y=600,label='帳單查詢',leaf=True,at=[c,1]),
 dict(id='fix',x=900,y=600,label='哪裡壞了？',at=d),dict(id='s',x=680,y=770,label='轉接：螢幕維修',leaf=True,at=f),dict(id='p',x=1140,y=770,label='轉接：開機問題',leaf=True,at=f)],
 edges=[dict(a='r',b='zh',label='按 1'),dict(a='r',b='en',label='按 2'),dict(a='zh',b='bill',label='按 1'),dict(a='zh',b='fix',label='按 2'),dict(a='fix',b='s',label='按 1'),dict(a='fix',b='p',label='按 2')],
 path=[dict(ids=['r','zh','fix','s'],at=e)])
E('card',x=1350,y=580,w=420,h=150,title='倒過來的樹',ts=32,col='OK',body=['開頭在最上面','越往下分岔越多'],bs=26,at=g)
# ---------- nodes
ep.scene('nodes','名詞：三種節點',chapter='名詞：根節點、內部節點、葉節點',desc='一棵樹標出根、內部、葉三種節點，三張說明卡逐一出現',ref='PART03 p39')
a=L('我們先幫樹上的每個方塊取名字。樹上的每一個方塊，叫做「節點」，英文是 node。')
b=L('最上面、整棵樹的起點，就像大樓的大門，只有出去的路，沒有進來的路。')
c=L('它叫做「根節點」，英文是 root node。')
d=L('中間那些還在問問題的節點，有一條路進來，又有兩條以上的路出去，就像走廊上的岔路口。')
e=L('它們叫做「內部節點」，英文是 internal node。')
f=L('最底下不再問問題、直接給答案的節點，就像走到最後的房間，只有進來、沒有出去。')
g=L('它們叫做「葉節點」，英文是 leaf node，也叫終端節點 terminal node。')
h=L('記一句話就好：根是起點，內部節點在問問題，葉子在給答案。')
E('tree',nodes=[dict(id='r',x=520,y=280,label='問題 1',at=a),dict(id='i1',x=300,y=470,label='問題 2',at=a),dict(id='l1',x=740,y=470,label='答案 A',leaf=True,at=a),
 dict(id='l2',x=160,y=660,label='答案 B',leaf=True,at=a),dict(id='l3',x=440,y=660,label='答案 C',leaf=True,at=a)],
 edges=[dict(a='r',b='i1'),dict(a='r',b='l1'),dict(a='i1',b='l2'),dict(a='i1',b='l3')],
 hl=[dict(id='r',at=b,until=d,col='A'),dict(id='i1',at=d,until=f,col='PUR'),dict(id='l1',at=f,until=h,col='B'),dict(id='l2',at=f,until=h,col='B'),dict(id='l3',at=f,until=h,col='B')])
E('card',x=940,y=210,w=830,h=170,title='根節點　root node',sub='起點・沒有進來的路，只有出去的路',col='A',at=c,body=['像大樓的大門'],bs=26)
E('card',x=940,y=400,w=830,h=170,title='內部節點　internal node',sub='一條路進來・兩條以上出去',col='PUR',at=e,body=['像走廊的岔路口：還在問問題'],bs=26)
E('card',x=940,y=590,w=830,h=170,title='葉節點　leaf / terminal node',sub='只進不出・給出答案（類別）',col='B',at=g,body=['像走到底的房間'],bs=26)
E('chips',y=840,items=[dict(s='根＝起點　內部＝問問題　葉＝給答案',col='OK',at=h)],size=30)
# ---------- test condition
ep.scene('test','名詞：測試條件與類別標籤',chapter='名詞：測試條件、分支、類別標籤',desc='講義的脊椎動物例子：體溫 → 是否胎生 → 哺乳類／非哺乳類',ref='PART03 p40–41')
a=L('那每個節點上「問的問題」，要叫什麼呢？')
b=L('講義用了一個動物分類的例子：判斷一種動物是不是哺乳類。')
c=L('根節點問的是：牠的體溫是恆溫，還是變溫？')
d=L('這種「拿某一個特徵出來問一個問題」的寫法，叫做「測試條件」，英文是 attribute test condition。')
e=L('一個問題有幾種可能的回答，就會長出幾條路。這些路叫做「分支」，英文是 branch。')
f=L('體溫有恆溫、變溫兩種答案，所以根節點長出兩條分支。')
g=L('變溫的那邊，直接走到葉子：非哺乳類。')
h=L('恆溫的那邊還不能確定，所以再問一題：是胎生的嗎？是，就是哺乳類；不是，就是非哺乳類。')
i=L('每一片葉子上寫的答案，就叫「類別標籤」，英文是 class label。')
j=L('通常每個測試條件只看一個特徵，這點後面幾集會一直用到。')
E('tree',nodes=[dict(id='r',x=560,y=280,label='體溫？',sub='Body Temperature',at=c),dict(id='gb',x=330,y=500,label='胎生嗎？',sub='Gives Birth',at=h),
 dict(id='nm',x=800,y=500,label='非哺乳類',leaf=True,at=g),dict(id='m',x=170,y=720,label='哺乳類',leaf=True,at=[h,2]),dict(id='nm2',x=490,y=720,label='非哺乳類',leaf=True,at=[h,3])],
 edges=[dict(a='r',b='gb',label='恆溫',at=f),dict(a='r',b='nm',label='變溫',at=f),dict(a='gb',b='m',label='是',at=[h,2]),dict(a='gb',b='nm2',label='否',at=[h,3])],
 hl=[dict(id='r',at=d,until=e,col='A'),dict(id='m',at=i,col='B'),dict(id='nm',at=i,col='B'),dict(id='nm2',at=i,col='B')])
E('card',x=1060,y=210,w=710,h=170,title='測試條件',sub='attribute test condition',col='A',at=d,body=['拿一個特徵出來問一個問題'],bs=26)
E('card',x=1060,y=400,w=710,h=170,title='分支',sub='branch',col='CY',at=e,body=['每一種回答 → 一條路'],bs=26)
E('card',x=1060,y=590,w=710,h=170,title='類別標籤',sub='class label',col='B',at=i,body=['葉子上寫的答案'],bs=26)
E('chips',y=840,cx=1415,items=[dict(s='一個測試條件通常只看一個特徵',col='DIM',at=j)],size=26)
# ---------- data
ep.scene('data','講義的例子：貸款會不會違約？',chapter='講義例子：貸款違約資料',desc='10 筆貸款資料表，特徵欄與標籤欄分色',ref='PART03 p42')
a=L('接下來看講義最重要的例子，這份資料在後面好幾集都會出現，請你一定要熟悉它。')
b=L('銀行有十位借過錢的客戶，每一列是一位客戶。')
c=L('前面三欄是特徵：有沒有自己的房子、婚姻狀況、還有年收入。')
d=L('最後一欄是標籤：這位客戶後來有沒有違約，也就是有沒有還不出錢。')
e=L('十個人裡面，有七個人沒有違約，三個人違約了。')
f=L('銀行想要的，是一套規則：下次有新客戶來申請，先猜猜看他會不會違約。')
g=L('這套規則，就可以用一棵決策樹來表示。')
rows=[['1','Yes','Single','125K','No'],['2','No','Married','100K','No'],['3','No','Single','70K','No'],['4','Yes','Married','120K','No'],['5','No','Divorced','95K','Yes'],['6','No','Married','60K','No'],['7','Yes','Divorced','220K','No'],['8','No','Single','85K','Yes'],['9','No','Married','75K','No'],['10','No','Single','90K','Yes']]
E('table',x=150,y=200,ws=[90,220,240,220,230],head=['ID','有房子 Home Owner','婚姻 Marital','年收入 Income','違約 Defaulted'],rows=rows,rh=56,hh=62,fs=28,at=b,
  hl=[dict(cols=[1,3],col='A',at=c,until=d),dict(cols=[4,4],col='B',at=d,until=e)],fills=[dict(row=r,col='BAD',at=e) for r in (4,7,9)])
E('card',x=1220,y=200,w=550,h=150,title='特徵 x',sub='有房子・婚姻・年收入',col='A',at=c)
E('card',x=1220,y=370,w=550,h=150,title='標籤 y',sub='有沒有違約（Yes／No）',col='B',at=d)
E('card',x=1220,y=540,w=550,h=150,title='No 7 位　Yes 3 位',sub='記成 (7, 3)',col='BAD',at=e,subMono=True)
E('card',x=1220,y=710,w=550,h=110,title='目標：新客戶來了，先猜',ts=30,col='OK',at=f)
# ---------- model
ep.scene('model','從資料長出的模型：一棵決策樹',chapter='這份資料長出的決策樹',desc='講義 p42 的決策樹：Home Owner → MarSt → Income，逐一核對訓練資料',ref='PART03 p42')
a=L('這是講義上，根據這十筆資料做出來的決策樹。')
b=L('根節點先問：有沒有自己的房子？')
c=L('有房子的話，直接走到葉子：不會違約。資料裡有房子的三個人，確實都沒有違約。')
d=L('沒有房子的話，再問：婚姻狀況是什麼？')
e=L('已婚的，走到葉子：不會違約。資料裡沒有房子又已婚的三個人，也都沒有違約。')
f=L('單身或離婚的，還要再問最後一題：年收入有沒有超過八萬？')
g=L('低於八萬，不會違約；高於八萬，會違約。')
h=L('你可以拿資料表一筆一筆對對看，十個人全部都被分到正確的葉子。')
i=L('在這棵樹裡，有房子、婚姻、年收入這三個特徵，就叫做「分裂屬性」，英文是 splitting attributes，也就是用來把資料分開的特徵。','在這棵樹裡，有房子、婚姻、年收入這三個特徵，就叫做「分裂屬性」，英文是 splitting attributes，也就是用來把資料分開的特徵。')
TREE=[dict(id='h',x=760,y=270,label='有房子？',sub='Home Owner',at=b),dict(id='y1',x=480,y=450,label='NO',leaf=True,at=c),dict(id='ms',x=1040,y=450,label='婚姻？',sub='MarSt',at=d),
 dict(id='y2',x=1320,y=630,label='NO',leaf=True,at=e),dict(id='inc',x=760,y=630,label='年收入？',sub='Income',at=f),dict(id='y3',x=560,y=810,label='NO',leaf=True,at=g),dict(id='y4',x=960,y=810,label='YES',leaf=True,at=g,col='BAD')]
EDG=[dict(a='h',b='y1',label='Yes'),dict(a='h',b='ms',label='No'),dict(a='ms',b='y2',label='Married'),dict(a='ms',b='inc',label='Single, Divorced'),dict(a='inc',b='y3',label='< 80K'),dict(a='inc',b='y4',label='> 80K')]
E('tree',nodes=TREE,edges=EDG,hl=[dict(id='h',at=i,col='A'),dict(id='ms',at=i,col='A'),dict(id='inc',at=i,col='A')])
E('card',x=150,y=200,w=380,h=170,title='ID 1・4・7',sub='有房子 → 全部 No',col='OK',at=[c,1.5],ts=30)
E('card',x=1330,y=250,w=440,h=170,title='ID 2・6・9',sub='沒房子＋已婚 → 全部 No',col='OK',at=[e,1.5],ts=30)
E('card',x=1180,y=740,w=590,h=140,title='ID 3：70K → No　✓',sub='ID 5・8・10：> 80K → Yes　✓',col='OK',at=h,ts=30)
E('chips',y=200,cx=1550,items=[dict(s='splitting attributes',col='A',at=i)],size=24)
# ---------- walk
ep.scene('walk','手算例題：新客戶走一遍',chapter='手算例題：把新客戶走到葉子',desc='測試資料 (No, Married, 80K)：從根節點一步步亮起路徑，最後指定 Defaulted = No',ref='PART03 p44–49')
a=L('好，現在來了一位新客戶，我們不知道他會不會違約。')
b=L('他沒有房子，已婚，年收入八萬。')
c=L('第一步，永遠從根節點開始。根節點問：有沒有房子？')
d=L('他沒有房子，所以走右邊「No」這條分支。')
e=L('第二步，來到婚姻這個節點。他是已婚，所以走「Married」這條分支。')
f=L('第三步，我們走到了葉子，葉子上寫著：NO。')
g=L('所以模型的判斷是：這位客戶不會違約。講義上寫的就是：把 Defaulted 指定為 No。')
h=L('注意，他的年收入八萬，在這條路上根本沒有被問到。決策樹只問路上會遇到的問題。')
E('table',x=150,y=200,ws=[200,200,200,200],head=['Home Owner','Marital','Income','Defaulted'],rows=[['No','Married','80K','?']],rh=60,hh=56,fs=30,at=b,cellCol=[dict(row=0,col=3,c='OK',at=g)])
E('tree',nodes=[dict(id='h',x=760,y=410,label='有房子？',sub='Home Owner'),dict(id='y1',x=480,y=560,label='NO',leaf=True),dict(id='ms',x=1040,y=560,label='婚姻？',sub='MarSt'),
 dict(id='y2',x=1320,y=710,label='NO',leaf=True),dict(id='inc',x=760,y=710,label='年收入？',sub='Income'),dict(id='y3',x=560,y=850,label='NO',leaf=True),dict(id='y4',x=960,y=850,label='YES',leaf=True,col='BAD')],
 edges=EDG,at=a,nh=70,path=[dict(ids=['h'],at=c),dict(ids=['h','ms'],at=d),dict(ids=['ms','y2'],at=f)])
E('card',x=1000,y=200,w=770,h=130,title='目前位置',ts=26,col='LINE',at=c,until=e,body=[dict(s='① 根節點：有房子？→ No',col='A')],bs=28)
E('card',x=1000,y=200,w=770,h=130,title='目前位置',ts=26,col='LINE',at=e,until=f,body=[dict(s='② 婚姻？→ Married',col='A')],bs=28,fill='#161a21')
E('card',x=1000,y=200,w=770,h=130,title='目前位置',ts=26,col='OK',at=f,body=[dict(s='③ 葉子：Defaulted ＝ No',col='OK')],bs=28,fill='#161a21')
E('chips',y=470,cx=1500,items=[dict(s='80K 這題沒被問到',col='B',at=h)],size=26)
# ---------- practice
ep.scene('practice','換你走走看',chapter='練習：再走兩位客戶',desc='兩位新客戶，暫停後揭曉路徑',ref='PART03 p44–49')
a=L('換你試試看。第二位客戶：沒有房子、離婚、年收入十二萬。可以先暫停想一想。',gap=2.5)
b=L('沒有房子，走 No；離婚，走「單身或離婚」；年收入十二萬，大於八萬，所以走到 YES：會違約。')
c=L('第三位客戶：有房子、單身、年收入五萬。',gap=2.0)
d=L('第一題就有答案了：有房子，直接走到葉子 NO，不會違約。後面兩題都不用問。')
e=L('你看，有的人要問三題，有的人一題就結束，這就是決策樹很有效率的地方。')
E('tree',nodes=[dict(id='h',x=560,y=280,label='有房子？'),dict(id='y1',x=300,y=440,label='NO',leaf=True),dict(id='ms',x=820,y=440,label='婚姻？'),
 dict(id='y2',x=1080,y=600,label='NO',leaf=True),dict(id='inc',x=560,y=600,label='年收入？'),dict(id='y3',x=380,y=760,label='NO',leaf=True),dict(id='y4',x=740,y=760,label='YES',leaf=True,col='BAD')],
 edges=EDG,at=a,nh=66,path=[dict(ids=['h','ms','inc','y4'],at=b,until=c),dict(ids=['h','y1'],at=d)])
E('card',x=1200,y=220,w=570,h=200,title='客戶 2',sub='No・Divorced・120K',col='A',at=a,subMono=True,body=[dict(s='→ YES（會違約）',col='BAD',at=b,w=700)],bs=32)
E('card',x=1200,y=450,w=570,h=200,title='客戶 3',sub='Yes・Single・50K',col='A',at=c,subMono=True,body=[dict(s='→ NO（一題就結束）',col='OK',at=d,w=700)],bs=32)
E('card',x=1200,y=680,w=570,h=120,title='最多問 3 題就有答案',ts=30,col='OK',at=e)
# ---------- another tree
ep.scene('another','同一份資料，可以長出不同的樹',chapter='同一份資料，不只一棵樹',desc='講義 p43：以 MarSt 為根的另一棵樹，與原本的樹並排',ref='PART03 p43')
a=L('這裡有一個很重要的觀念。講義上還畫了另一棵樹。')
b=L('這次根節點先問婚姻：已婚的，直接 NO。')
c=L('單身或離婚的，再問有沒有房子；有房子就 NO，沒有房子再看年收入。')
d=L('拿這十筆資料去對，這棵樹一樣全部答對。')
e=L('講義寫得很清楚：同一份資料，可能有不只一棵樹都能符合。')
f=L('那問題就來了：到底該先問哪一題？哪一棵樹比較好？')
g=L('這正是接下來兩集要回答的：下一集看樹是怎麼一步步長出來的，再下一集學怎麼挑「最好的問題」。')
E('text',s='樹 A（講義 p42）',x=470,y=215,size=26,col='DIM',w=700,align='center',at=a)
E('tree',at=a,nh=64,nodes=[dict(id='h',x=470,y=290,label='有房子？'),dict(id='y1',x=260,y=430,label='NO',leaf=True),dict(id='ms',x=650,y=430,label='婚姻？'),dict(id='y2',x=820,y=570,label='NO',leaf=True),dict(id='inc',x=470,y=570,label='年收入？'),dict(id='y3',x=330,y=710,label='NO',leaf=True),dict(id='y4',x=610,y=710,label='YES',leaf=True,col='BAD')],
 edges=[dict(a='h',b='y1',label='Yes'),dict(a='h',b='ms',label='No'),dict(a='ms',b='y2',label='M'),dict(a='ms',b='inc',label='S, D'),dict(a='inc',b='y3',label='<80K'),dict(a='inc',b='y4',label='>80K')])
E('text',s='樹 B（講義 p43）',x=1400,y=215,size=26,col='DIM',w=700,align='center',at=b)
E('tree',at=b,nh=64,nodes=[dict(id='ms',x=1400,y=290,label='婚姻？'),dict(id='y1',x=1640,y=430,label='NO',leaf=True),dict(id='h',x=1210,y=430,label='有房子？',at=c),dict(id='y2',x=1040,y=570,label='NO',leaf=True,at=c),dict(id='inc',x=1380,y=570,label='年收入？',at=c),dict(id='y3',x=1250,y=710,label='NO',leaf=True,at=c),dict(id='y4',x=1510,y=710,label='YES',leaf=True,col='BAD',at=c)],
 edges=[dict(a='ms',b='y1',label='M'),dict(a='ms',b='h',label='S, D'),dict(a='h',b='y2',label='Yes'),dict(a='h',b='inc',label='No'),dict(a='inc',b='y3',label='<80K'),dict(a='inc',b='y4',label='>80K')])
E('chips',y=790,items=[dict(s='兩棵樹都 10 筆全對 ✓',col='OK',at=d)],size=28)
E('chips',y=860,items=[dict(s='More than one tree can fit the same data!',col='B',at=e)],size=26)
# ---------- rules
ep.scene('rules','決策樹＝一串 IF–THEN 規則',chapter='把樹翻成 IF–THEN 規則',desc='每條從根到葉的路徑變成一條規則',ref='PART03 p127')
a=L('決策樹還有一個大優點：很容易解釋。')
b=L('從根走到每一片葉子的路，都可以翻成一句「如果……就……」的規則，英文叫 IF–THEN rule。','從根走到每一片葉子的路，都可以翻成一句「如果……就……」的規則，英文叫 if then rule。')
c=L('例如：如果有房子，就不會違約。')
d=L('如果沒有房子，而且已婚，也不會違約。')
e=L('如果沒有房子、單身或離婚、年收入高於八萬，就會違約。')
f=L('四片葉子，就是四條規則。銀行員就算不懂機器學習，也看得懂這張表。')
E('bullets',x=150,y=220,w=1620,size=32,items=[dict(s='IF　有房子　THEN　No',at=c,col='OK'),dict(s='IF　沒房子 AND 已婚　THEN　No',at=d,col='OK'),dict(s='IF　沒房子 AND 單身或離婚 AND 年收入 < 80K　THEN　No',at=[e,-0.5],col='OK'),dict(s='IF　沒房子 AND 單身或離婚 AND 年收入 > 80K　THEN　Yes',at=e,col='BAD')])
E('chips',y=780,items=[dict(s='4 片葉子 ＝ 4 條規則',col='A',at=f),dict(s='容易解釋 interpretable',col='OK',at=[f,1])],size=30)
# ---------- mistakes
ep.scene('mistakes','常見誤區',chapter='常見誤區',desc='四張紅色警示卡',ref='PART03 p39–43')
a=L('最後整理幾個新手最常搞混的地方。')
b=L('第一，葉子不問問題。問問題的是根節點和內部節點；葉子只負責給答案。')
c=L('第二，一定要從根節點開始，一題一題往下走，不能跳著問。')
d=L('第三，不是每個特徵都會被問到。剛剛那位已婚客戶，年收入就完全沒用上。')
e=L('第四，注意邊界。講義寫的是小於八萬和大於八萬，那剛好等於八萬怎麼辦？')
f=L('實務上我們會寫成「小於等於」和「大於」，讓每一筆資料都只有一條路可以走。')
g=L('第五，樹不是唯一的。同一份資料可以有好幾棵樹，所以才需要方法去挑。')
E('bullets',x=150,y=210,w=1620,size=30,gap=12,items=[dict(s='葉子不問問題：根節點、內部節點問問題；葉子給答案',at=b,col='BAD'),dict(s='一定從根開始、一層一層往下走，不能跳題',at=c,col='BAD'),
 dict(s='不是每個特徵都會被用到（已婚客戶沒被問年收入）',at=d,col='BAD'),dict(s='邊界要說清楚：「< 80K／> 80K」漏掉剛好 80K → 寫成 ≤ 80K／> 80K',at=e,col='BAD'),dict(s='樹不是唯一的：同一份資料可以長出好幾棵樹',at=g,col='BAD')])
E('chips',y=860,items=[dict(s='每筆資料只能有一條路',col='OK',at=f)],size=26)
# ---------- quiz
ep.scene('quiz','小測驗',chapter='小測驗',desc='三題，倒數暫停後揭曉')
L('來個小測驗，可以先暫停想一想。')
q1=L('第一題：只有進來的路、沒有出去的路，負責給答案的節點，叫做什麼？',gap=3.0)
a1=L('答案是葉節點，英文是 leaf node。')
q2=L('第二題：用講義的樹，沒有房子、單身、年收入六萬的客戶，會被判斷成什麼？',gap=3.0)
a2=L('沒有房子走 No，單身走單身或離婚，六萬小於八萬，所以是 NO，不會違約。')
q3=L('第三題：同一份資料，只能長出一棵決策樹，對還是錯？',gap=3.0)
a3=L('錯。同一份資料可以長出好幾棵都符合的樹，所以我們需要方法來挑。')
E('quiz',y=215,qs=[dict(q='Q1　只進不出、負責給答案的節點叫什麼？',a='葉節點 leaf node',qi=q1,ai=a1),dict(q='Q2　No 房子・Single・60K 會被判成？',a='NO（No → 單身 → 60K < 80K）',qi=q2,ai=a2),dict(q='Q3　同一份資料只能長出一棵樹？',a='錯：可以有好幾棵，要靠方法挑',qi=q3,ai=a3)])
# ---------- recap
ep.scene('recap','重點回顧',chapter='重點回顧與下集預告',desc='四點回顧＋下集預告卡')
a=L('今天的重點整理一下。')
b=L('決策樹，就是用一連串是非題做判斷的模型，像玩猜猜我是誰。')
c=L('三種節點：根節點是起點，內部節點問問題，葉節點給答案，也就是類別標籤。')
d=L('每個問題叫測試條件，通常只看一個特徵；每種回答長出一條分支。')
e=L('判斷新資料：從根出發，照答案一路往下走，走到葉子就是結果。')
f=L('這也是作業一的前置知識。下一集，我們要學 Hunt\'s 演算法：一棵樹到底是怎麼從資料裡一步步長出來的。我們下集見！','這也是作業一的前置知識。下一集，我們要學杭特演算法：一棵樹到底是怎麼從資料裡一步步長出來的。我們下集見！')
E('bullets',x=160,y=220,w=1600,size=32,items=[dict(s='決策樹：用一連串是非題做判斷的模型',at=b),dict(s='根節點＝起點・內部節點＝問問題・葉節點＝給答案（類別標籤）',at=c),dict(s='測試條件：通常只看一個特徵；每種回答 → 一條分支',at=d),dict(s='新資料：從根出發 → 照答案往下走 → 走到葉子',at=e)])
E('card',x=160,y=720,w=1600,h=110,title='下一集 EP14：Hunt\'s 演算法：一步步長出決策樹（作業一）',ts=34,col='A',align='center',at=f,fill='#11161d')
ep.save('.')

# 範例集（煙霧測試用，約 40 秒，3 個場景）。執行：python make_episode.py episodes/sample
# 這個檔案定義「腳本＋畫面」：L() 是一句旁白（同時是燒錄字幕），E() 是一個畫面元素，at= 指定它跟著哪一句出現。
from lib import Ep          # make_episode.py 會把 kit/ 加進 PYTHONPATH，不需要寫絕對路徑
ep = Ep(99, '範例：什麼是特徵與標籤？', '',
        '這是 ml-video-kit 的範例集，用三個場景示範標題卡、表格與小測驗。',
        ['機器學習', '範例', '特徵', '標籤', '機器學習從零開始'], 'EP01 機器學習是什麼')
E = ep.E; L = ep.L

# ---------- 場景 1：標題卡
ep.scene('title', '', noHeader=True, chapter='開場', desc='標題卡')
E('titlecard', ep='EP99 · 範例集', title='特徵與標籤', sub='三個場景的煙霧測試')
L('嗨，這是一支範例影片，用來確認整條產線可以正常運作。')

# ---------- 場景 2：表格
ep.scene('table', '一筆資料長什麼樣子', chapter='特徵與標籤', desc='表格：特徵欄位與標籤欄位', ref='PART01 p27')
a = L('表格裡的每一列是一筆資料，前面幾欄叫做特徵。')
b = L('最後一欄是我們想預測的答案，叫做標籤。', '最後一欄是我們想預測的答案，叫做標籤。')
E('table', x=360, y=260, ws=[300, 300, 300, 300], head=['有連結', '免費字數', '寄件人認識', '垃圾信？'],
  rows=[['有', '3', '否', '是'], ['沒有', '0', '是', '否']], at=a, cellCol=[dict(row=0, col=3, c='BAD', at=b), dict(row=1, col=3, c='OK', at=b)])
E('hl', x=1260, y=255, w=300, h=190, col='B', at=b)
E('chips', y=560, items=[dict(s='特徵 feature', col='A', at=a), dict(s='標籤 label', col='B', at=b)], size=30)

# ---------- 場景 3：小測驗
ep.scene('quiz', '小測驗', chapter='小測驗', desc='一題測驗，倒數後顯示答案')
q = L('小測驗：我們想預測的那一欄叫做什麼？', gap=1.0)
ans = L('答案是標籤。範例影片到這裡結束，謝謝收看！')
E('quiz', y=260, qs=[dict(q='Q1　想預測的那一欄叫做什麼？', a='標籤 label', qi=q, ai=ans)])

ep.save('.')

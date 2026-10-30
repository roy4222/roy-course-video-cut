# 集數腳本格式

一集 = 一個資料夾。套件只要求裡面有 `build.py`。`make_episode.py` 會把 `windows-kit/kit` 放進 `PYTHONPATH`，所以直接寫：

```python
from lib import Ep
```

EP11–EP20 的舊稿第一行還有 `sys.path.insert(...)`。現在它會先看環境變數 `EP_ENGINE`，沒有就用當天的路徑。用套件跑的時候，那一行找不到目錄也沒關係，真正用到的是套件裡的 `lib.py`。新的一集照下面的範例寫，不必加那一行。

## 最小的一集

存成 `episodes/ep21/build.py`，在 `windows-kit` 裡執行 `make_episode` 時把這個資料夾傳進去。

```python
from lib import Ep

ep = Ep(
    21,                          # 集數。成片檔名會是 ep21.mp4
    "標題：這集在講什麼",
    "",                          # 頁首。空字串 = 自動「EP21 · 標題」
    "一兩句摘要，會放進 YouTube 說明。",
    ["機器學習", "這集的關鍵詞", "機器學習從零開始"],
    "下集預告：下一集的一句話",
)
E = ep.E
L = ep.L

ep.scene("title", "", noHeader=True, chapter="開場", desc="標題卡")
E("titlecard", ep="EP21 · 單元名", title="這集的標題", sub="一句副標")
L("嗨，歡迎回到機器學習補習班。這是第二十一集。")

ep.scene("idea", "先用生活例子看一次", chapter="直覺", desc="先講比喻，再給名稱", ref="講義頁碼")
a = L("想像你在整理衣櫃：先把很不像的衣服分開。")
b = L("這個動作的正式名稱叫分類。英文是 classification。", gap=0.4)
E("card", x=150, y=240, w=720, h=160, title="先講人話", col="A", at=a)
E("card", x=1000, y=240, w=720, h=160, title="再給名稱：分類 classification", col="B", at=b)

ep.save(".")
```

`ep.save(".")` 一定要有。它會寫出四個 json，並檢查每個 `at` / `until` 有沒有指到這個場景裡存在的句子。

`Ep` 的參數依序是：集數、標題、頁首、摘要、標籤清單、下集預告。最後還可以加 `accent='A'`（進度條和頁首那條線的顏色，預設藍）。

## 句子 `L`

```python
i = L("畫面上的字幕，也是預設的念法。")
j = L("字幕寫 83.8%", "念成：百分之八十三點八")   # 第二個參數是 say
k = L("停久一點，讓觀眾看表。", gap=1.5)         # 這句結束後多停的秒數
```

- 回傳值是**這個場景裡**的句子編號，從 0 開始。下一個 `ep.scene(...)` 會重新從 0 數。
- `say` 給數字、英文、破音字。畫面仍顯示第一個參數。
- 數字可以借用 `from zh import zh, pct`。`zh(83.8)` 會變成「八十三點八」。

## 場景 `scene`

```python
ep.scene(
    "hook",                    # id，英文短名，給檔案和除錯用
    "場景標題",                 # 畫在頁首
    chapter="YouTube 章節名",   # 沒寫就用場景標題
    desc="這幕在講什麼，會進 script.md",
    ref="講義 PART03 p38",
    tag="作業一",               # 右上角小標，可省略
    tagCol="B",
    noHeader=True,             # 標題卡那一幕用
)
```

空場景（一句台詞都沒有）存檔時會失敗。

## 元素什麼時候出現

`at` 和 `until` 都是「這個場景裡的句子編號」，或 `[編號, 再延後幾秒]`。

- `at=i`：第 i 句開始時淡入
- `at=[i, 1.2]`：第 i 句開始後再等 1.2 秒
- `at=-1`：場景一開始就出現
- `until=k`：到第 k 句時淡出

畫布是 1920×1080。頁首大約佔到 y=170。字幕大約在 y>900。內容放在 y=200 到 880 比較安全。左右留大約 150。

顏色名字：`A` 藍、`B` 橘、`OK` 綠、`BAD` 紅、`PUR` 紫、`CY` 青、`INK` 白、`DIM` 灰。也可以直接寫 `'#rrggbb'`。

## 元素種類

完整繪製在 `windows-kit/engine/engine.js`。下表是 `E("名字", ...)` 常用的參數。

| type | 你會用到的參數 | 適合 |
|---|---|---|
| `titlecard` | `ep, title, sub` | 片頭 |
| `text` | `s, x, y, size, col, w, align, wrap, mono` | 一行或一段字。`wrap` 是寬度，會自動換行 |
| `card` | `x, y, w, h, title, sub, body, col, align` | 卡片 |
| `bullets` | `x, y, w, size, items=[{s, at, col}]` | 編號條列 |
| `chips` | `y, items=[{s, col, at}], size, cx` | 一排小標籤 |
| `table` | `x, y, ws, head, rows, rowAt, cellCol` | 表格。可以逐列出現、儲存格上色 |
| `formula` | `x, y, w, lines, label, size` | 公式或計算步驟 |
| `tree` | `nodes=[{id,x,y,label,leaf,at}]`, `edges`, `path` | 決策樹。`path` 可以把一條路照亮 |
| `flow` | `x, y, w, items=[{s, sub, col, at}]` | 橫向流程 |
| `blocks` | `x, y, rows=[{cells, at}]` | 切資料、分組 |
| `arrow` / `line` | `x1, y1, x2, y2, col` | 箭頭、線 |
| `bars` | `x, y, w, h, max, items=[{label, v, col, at}]` | 長條圖 |
| `plot` / `dots` / `circle` | 座標範圍 `xr, yr`，或圓心半徑 | 散佈、點、圓 |
| `code` | `x, y, w, h, title, cells=[{code, out, at}]` | 程式畫面 |
| `quiz` | `y, qs=[{q, a, qi, ai}]` | 小測驗。`qi` 是題目那句，`ai` 是答案那句 |
| `hl` / `check` / `cross` | 框的 `x, y, w, h`，或勾叉的 `x, y, s` | 螢光框、對、錯 |

看一整集怎麼串，打開 `windows-kit/episodes/ep13-example/build.py` 或 `episodes/ep14/build.py`。

## 舊的 `src.py`（EP00–EP10）

那些集的來源是 `src.py`，裡面有 `META`（字典）和 `SCENES`（清單）。畫面描述用另一套 `v: [{k: 'cards', ...}]`，由 `legacy/pipeline_A/engine.js` 畫。**套件的 `engine.js` 讀不了這個格式。** 要重做，改寫成上面的 `build.py`。已生成的 `script.json`、`scenes.json` 可以留著對稿。

## 加一種新的畫面元素

假設要加一種「兩欄對照」，名字叫 `compare`。

1. 打開 `windows-kit/engine/engine.js`。找到 `const R={};` 下面一排 `R.text=`、`R.card=`。照同樣的形狀加一個函式：

   ```javascript
   R.compare = (t, e, a) => {
     // t = 現在的秒數，e = build.py 傳進來的那包參數，a = 0到1的透明度
     // 畫字請用已經寫好的 T(...) 或 para(...)。它們會在版面檢查時回報文字框。
   };
   ```

2. 透明度、淡入淡出不用自己算。引擎在呼叫你之前已經用 `at` / `until` 算出 `a`。你要把 `a` 乘進你畫的東西（現有的 `box`、`T` 會幫你乘）。

3. 在某一集的 `build.py` 裡試：

   ```python
   E("compare", x=150, y=240, w=1620, h=400, left="人話", right="正式名稱", at=a)
   ```

4. 先不要配音。只跑：

   ```text
   make_episode.cmd <集數資料夾> build timeline stills
   ```

   看 `qc/pre/` 的預覽，以及 `qc/layout.txt` 有沒有 OUT-OF-FRAME、OVERLAP、UNDER-SUBTITLE。

5. 在 [這份文件的元素表](#元素種類) 加一列，讓下一次的你還記得參數。

`window.TEXTS(t)` 會把畫面上的文字框收集起來給版面檢查。若你的新元素用 `T()` 畫字，檢查會自動看得到。若你用 canvas 的 `fillText` 直接畫，檢查就看不到它，重疊也不會被提醒。

存檔時 `lib.py` 會檢查 `at`、`until`、`qi`、`ai`、`hot`、`oat` 這幾個欄位是不是合法的句子編號。新元素若有「跟著某一句出現」的欄位，沿用 `at` 這個名字，檢查才會幫你。

## 數字從哪來

EP17、EP18、EP20 的圖上數字來自 `episodes/_worked_examples/` 裡事先算好的 json。`build.py` 會先找這個資料夾（或環境變數 `WORKED_EXAMPLES`），找不到才回到當天的絕對路徑。那些 json 是手算或小程式的結果，不是講義 PDF。講義本身沒有放在這個倉庫。

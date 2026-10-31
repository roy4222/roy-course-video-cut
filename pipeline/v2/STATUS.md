# STATUS.md 認領

多台機器一起做的時候，先改表，再動手。活的那張表放在 `$SEC_SERIES/STATUS.md`，不進 git。下面是協定，以及可以複製過去的範本。

## 狀態

| 標記 | 意思 |
|---|---|
| 認領 | 某一個角色正在做這一集。列上角色和時間。別人不要同時改同一集 |
| `READY` | 該集目錄有一個空檔 `READY`，而且 `script.md`、`meta.json` 都齊了。Lead 可以排渲染 |
| `ENHANCING` | 正在改腳本。不要渲染。原來的 `READY` 先改名成 `READY.v1hold` |
| 渲染中 | 已經拿走算圖。不要重跑配音，不要改 `build.py` |
| QC | 成片在 `out/`。閘門見 [RENDER.md](RENDER.md) |
| 已上傳 | Drive 和私人 YouTube 都有了。換版本之前先問 Boss |

## 做法

1. 先在自己的那一列寫下角色（桌機、Mac mini 或 box）和時間，再開始。
2. 腳本沒做完，不要放 `READY`。
3. 算圖的機器只領「READY、而且沒有人認領渲染」的集。
4. 桌機可以同時配好幾集音。NVENC 一次只渲染一集。Mac mini 和 box 用 CPU。box 記憶體大約 16GB，工人數維持在說明書的範圍裡，Chromium 才不會被殺掉。
5. MacBook 不認領配音，也不認領算圖。
6. 錄屏的 X 畫面號碼分段，不要兩個人用同一個號碼。分段見 [README](README.md)。
7. 刪 Drive 或 YouTube 上的舊版之前，先問 Boss。

當天改表用的小工具在 `tools/ready.py`、`tools/mark.py`、`tools/status.py`，以及 `align_qc/setrow.py`。它們認的是下面這種列文字，而且讀的是 `$SEC_SERIES/STATUS.md`。新的一輪直接改表就好，不必為了遷就腳本去造同樣的句子。

`setrow.py` 會把檔案裡以 `更新：` 開頭的那一行換成當天的時間。

## 範本

複製到 `$SEC_SERIES/STATUS.md`：

```markdown
更新：2026-10-31 14:00

| 集 | 狀態 |
|---|---|
| SEC11 | 認領：box 14:05 寫腳本 |
| SEC12 | ✅ READY |
| SEC13 | ⛔ ENHANCING (do not render) — 正在改 v2 腳本 |
```

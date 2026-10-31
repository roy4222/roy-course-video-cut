# 之後可以做的

系統與軟體安全（v2）下一版要處理的意見在 [`pipeline/v2/ROADMAP.md`](../pipeline/v2/ROADMAP.md)。這一頁仍是 v1 機器學習這一季。

v0.1（2026-10-30）做完了 EP00–EP20，以及實戰 A1、A2 上、A2 下，一共 24 支。下面是已經想過、還沒做的事。做的時候仍用 `windows-kit/`，不要再開第五套平行管線。

## 這一季剩下的集

`notes/season_plan.md` 後段列了講義還沒到齊時的暫定題目。順序跟著「先懂距離，才講 KNN」這種依賴，而不是跟著頁碼硬切。

| 集 | 暫定標題 | 大約長度 |
|---|---|---|
| EP21 | KNN：看鄰居投票（接 EP09 的距離） | 14 分 |
| EP22 | Logistic Regression：分數變成機率 | 16 分 |
| EP23 | SVM（一）：找一條最寬的分界 | 15 分 |
| EP24 | SVM（二）：軟間隔與參數 C | 15 分 |
| EP25 | SVM（三）：Kernel | 16 分 |
| EP26 | Ensemble（一）：Bagging 與隨機森林 | 16 分 |
| EP27 | Ensemble（二）：Boosting | 16 分 |
| EP28 | 期末總複習：一張圖串起整門課 | 15 分 |

開新的一集時，複製 `windows-kit/episodes/sample/build.py` 的形狀，依 [風格](style-guide.md) 寫。講義頁碼寫在場景的 `ref`，講義 PDF 不要放進 git。

## 舊集要不要重做

EP00–EP10 是 `src.py`。套件畫不出來。若要改一句旁白或一張圖，先把那一集改寫成 `build.py`（格式見 [集數腳本](episode-format.md)），再用套件重跑。已上傳的成片若只是小錯字，改說明比重做整集便宜。

## 工具本身

- 新的畫面元素只加在 `windows-kit/engine/engine.js`，並在文件的元素表補一列。先用 `build timeline stills` 看預覽，再配音。
- 8 核心的機器維持最多 2 個渲染工人；有 NVENC 的桌機維持一集渲染完再下一集。若以後換成不受工作階段上限的編碼器，再放寬 `queue*.ps1`，並在 CHANGELOG 寫下來。
- 範例集 `episodes/sample` 的旁白 wav 沒有進 git。若要做「不用金鑰的煙霧測試」，可以另外準備幾秒可再散布的測試音，放在不被 `.gitignore` 的 `*.wav` 規則擋掉的路徑之外，或在測試說明裡寫「這一步需要金鑰」。不要把整集成片推進 git。
- Noto 字型維持「腳本下載、不進 git」。若 clone 之後常忘記下載，可以在 `setup.ps1` / `setup.sh` 結尾印一行提醒，指向 `scripts/fetch_fonts`。
- `legacy/qc/final_qc.py` 的檢查（解析度、fps、片長對字幕）可以挑進套件的 `qc` 步驟。搬之前先用一集已完成的成片對一下它會不會誤報。

## 別的課

同一套 `Ep` 腳本和暗色架構圖可以拿去做別的入門課：一集 10–20 分鐘、每個名詞先用人話講一次、手算留在畫面上。實務上是：

1. 複製 `windows-kit/` 成一個新目錄，或繼續用這一棵，把新課的集數放在別的資料夾（`make_episode.py` 接受任何集數路徑）。
2. 改 `Ep(...)` 的系列名稱、標籤，以及 `make_episode.py` 裡 `yt` 步驟的那段固定介紹（搜尋「機器學習從零開始」）。
3. 聲音可以沿用 Enceladus，或先用 `legacy/tools/voice_test/` 的方式試聽再決定。
4. 新課若有學校或單位名稱，沿用現在的做法：標題和說明寫課程主題，不要寫單位名稱；上傳腳本的檢查留著。
5. 講義、作業全文、學員名單不要放進公開倉庫。可以另做一個不進 git 的對照表，或只放像 `coverage/` 這種「哪一頁被哪一集講到」的索引。

`coverage/build.py` 會用 openpyxl 產生 `coverage.xlsx`，記錄 PART00–PART03 的頁面範圍有沒有對到某一集。當天的結果是 511/511 頁都有對到某一集。那是索引，不是講義內容。

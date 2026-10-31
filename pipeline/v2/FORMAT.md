# 系統與軟體安全 · 一集怎麼交

做完一集，在該集目錄放一個空檔 `READY`。Lead 看到才會排渲染。沒做完不要放。

路徑用環境變數，不寫死某一台機器。設定方式見 [config.example.env](config.example.env)。

## 目錄（每一集）

```
$SEC_SERIES/epXX/              # XX = 00..39，兩位數字；加碼集可以用 epHX10 這種名字
  script.md                    # 必填：旁白和畫面指示
  meta.json                    # 必填：標題、摘要、來源、tags
  assets/                      # 圖片。檔名只能是 ASCII（英文、數字、底線、點）
    foo.png
    foo.credit.txt             # 一行：來源網址，加一句這張圖是什麼
  recordings/                  # 真的螢幕或終端錄影，10–90 秒最適合
    clip.mp4
  READY                        # 空檔。script.md 和 meta.json 都齊了才可以放
```

也可以把畫面直接寫成套件腳本，放在 `$KIT/episodes/secXX/build.py`。兩邊都有的時候，以 `script.md` 為準，由 Lead 轉成 `build.py`。寫的人優先交 `script.md`。

## meta.json

```json
{
  "num": 1,
  "title": "白帽怎麼賺錢？Bug Bounty 難不難",
  "short": "SEC01 · 白帽收入",
  "summary": "一句話說明這集帶走什麼（會進 youtube.json）",
  "tags": ["Bug Bounty", "白帽", "系統與軟體安全"],
  "next": "SEC02 手機怎麼不被看光",
  "sources": ["https://example.com/source"],
  "hook_segments": ["開場賞金數字", "中段真實案例"]
}
```

## script.md

```markdown
# SEC01 白帽怎麼賺錢？Bug Bounty 難不難

- 目標長度：12–14 分（旁白大約 2400–3000 字；節奏大約 220 字/分）
- 每句旁白：理想 30 字以內，硬上限 45 字（字幕要切成 18 字以內）
- 視覺類型（每一段標一個）：living-screencast | visual-investigation | whiteboard | ascii-crt | blueprint | iso-infographic | teardown | caption-news | titlecard

## 00. 開場
**畫面**：titlecard
**style**：titlecard
**assets**：—

- 嗨，這是系統與軟體安全第一集。
- 上一集用新聞把你勾進來。

## 01. 章節標題
**畫面**：一句話描述觀眾會看到什麼
**style**：caption-news
**assets**：assets/hackerone_report.png
**recording**：recordings/browse_h1.mp4
**來源角標**：https://www.hackerone.com/

- 短旁白一句。
- 再一句。
```

### 規則

1. 一行一個旁白句。不要寫 60 字以上的長句。
2. 字幕由管線切，每段最多 18 字。不要自己插時間碼。英文字、程式名稱、數字和它的單位要留在一起。
3. 每一分鐘至少兩種畫面。不要連續 60 秒都是同一種版型。
4. 鉤子要穿插，不只開場。大約最多 3 分鐘就要有一個：真實事故、CTF 的一下就懂、自己動手、賞金故事、機器人案例。那一段的 style 用 `caption-news` 或 `visual-investigation`，並寫進 `meta.hook_segments`。
5. 數字和事故要有可以點的來源。寫進 `meta.sources`，也寫在該段的「來源角標」。
6. 截圖檔名只用 ASCII。中文檔名換到另一台電腦會變成空畫面。每一張圖都要有同名的 `.credit.txt`。
7. 不做完整的武器化攻擊步驟、學校作業的官方解答、或未授權的攻擊教學。

## 畫面標籤

| 標籤 | 用途 |
|---|---|
| titlecard | 片頭 |
| cards / bullets / flow / table | 圖解 |
| cite | 底部來源 |
| living-screencast | 真的錄屏，優先放 `recordings/` |
| visual-investigation | 截圖加說明，檔案放 `assets/`，並加角標 |
| whiteboard / blueprint / iso-infographic / ascii-crt / teardown / caption-news | 風格。Lead 會對到卡片、流程或公式 |

## 長度

- 成片 10–15 分，理想 12–14 分
- 旁白大約每分鐘 220 個中文字
- 總字數大約 2500–3200
- 一集 8–14 個 `##` 場景

## 放 READY 之前

- [ ] `script.md` 在，而且每一句不超過 45 字
- [ ] `meta.json` 有 title、summary、sources
- [ ] 至少 3 張圖，或 1 段錄影（鉤子多的集再多一點）
- [ ] 每張截圖都有 `.credit.txt`，檔名是 ASCII
- [ ] 空檔 `READY` 只在做完之後才放

多台機器一起做的時候，先改 [`STATUS.md`](STATUS.md) 再動手。

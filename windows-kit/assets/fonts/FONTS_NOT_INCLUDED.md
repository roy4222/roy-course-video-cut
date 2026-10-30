`NotoSansCJKtc-Regular.woff2` 與 `NotoSansCJKtc-Bold.woff2` 是 `fonts.css` 要的繁中字型（大約 11 MB 與 12 MB）。
它們故意沒有放進 git。

請在倉庫根目錄執行：

```bash
bash scripts/fetch_fonts.sh
```

Windows：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_fonts.ps1
```

腳本會從官方 Noto CJK 發行檔下載 Traditional Chinese 的 Regular 與 Bold
（[notofonts/noto-cjk](https://github.com/notofonts/noto-cjk) release `Sans2.004` 的 `09_NotoSansCJKtc.zip`，SIL OFL 1.1），
轉成上面兩個 woff2 檔名，放到這個資料夾。授權全文會寫到 `windows-kit/licenses/NotoSansCJK-OFL.txt`。

同一個資料夾裡的 DejaVu Sans Mono（等寬、程式碼畫面用）已經在 git 裡，授權見 `windows-kit/licenses/DejaVu-license.txt`。

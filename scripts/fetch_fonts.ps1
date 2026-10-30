# 下載 Noto Sans CJK TC，轉成 windows-kit\assets\fonts\fonts.css 要用的 woff2。
# 官方來源：https://github.com/notofonts/noto-cjk （SIL Open Font License 1.1）
# 釘選發行檔：Sans2.004 / 09_NotoSansCJKtc.zip
# 不會把字型 commit 進 git。可以重複執行。
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_fonts.ps1
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Dest = Join-Path $Root 'windows-kit\assets\fonts'
$LicDir = Join-Path $Root 'windows-kit\licenses'
$Lic = Join-Path $LicDir 'NotoSansCJK-OFL.txt'
$ZipUrl = 'https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/09_NotoSansCJKtc.zip'
$LicUrl = 'https://raw.githubusercontent.com/notofonts/noto-cjk/Sans2.004/LICENSE'
$Reg = Join-Path $Dest 'NotoSansCJKtc-Regular.woff2'
$Bold = Join-Path $Dest 'NotoSansCJKtc-Bold.woff2'

New-Item -ItemType Directory -Force -Path $Dest, $LicDir | Out-Null

if (-not (Test-Path $Lic) -or (Get-Item $Lic).Length -eq 0) {
  Write-Host "下載授權 $LicUrl"
  curl.exe -fsSL $LicUrl -o $Lic
  if ($LASTEXITCODE -ne 0) { throw "下載授權失敗" }
}

if ((Test-Path $Reg) -and (Test-Path $Bold) -and (Get-Item $Reg).Length -gt 0 -and (Get-Item $Bold).Length -gt 0) {
  Write-Host "字型已經在 $Dest"
  Get-Item $Reg, $Bold | Format-Table Name, Length
  exit 0
}

$Py = $null
foreach ($c in @('python', 'py', 'python3')) {
  if (Get-Command $c -ErrorAction SilentlyContinue) { $Py = $c; break }
}
if (-not $Py) { throw '需要 Python 3，才能把 otf 轉成 woff2。' }

& $Py -c "import fontTools, brotli" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Host '安裝 fonttools 與 brotli（只用來轉檔，不會改系統字型）。'
  & $Py -m pip install --user 'fonttools>=4.40' 'brotli>=1.0'
  if ($LASTEXITCODE -ne 0) { throw 'pip 安裝 fonttools / brotli 失敗' }
}

$Tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("noto-cjk-" + [guid]::NewGuid().ToString('n'))
New-Item -ItemType Directory -Force -Path $Tmp | Out-Null
try {
  $Zip = Join-Path $Tmp 'noto.zip'
  Write-Host "下載官方 Noto Sans CJK TC（約 90 MB）"
  Write-Host "  $ZipUrl"
  curl.exe -fL --retry 3 -o $Zip $ZipUrl
  if ($LASTEXITCODE -ne 0) { throw '下載字型壓縮檔失敗' }

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  $archive = [System.IO.Compression.ZipFile]::OpenRead($Zip)
  try {
    $wanted = @('NotoSansCJKtc-Regular.otf', 'NotoSansCJKtc-Bold.otf')
    $got = @{}
    foreach ($entry in $archive.Entries) {
      $name = [System.IO.Path]::GetFileName($entry.FullName)
      if ($wanted -contains $name -and -not $got.ContainsKey($name)) {
        $out = Join-Path $Tmp $name
        [System.IO.Compression.ZipFileExtensions]::ExtractToFile($entry, $out, $true)
        $got[$name] = $out
      }
    }
  } finally { $archive.Dispose() }
  foreach ($name in @('NotoSansCJKtc-Regular.otf', 'NotoSansCJKtc-Bold.otf')) {
    if (-not $got.ContainsKey($name)) { throw "壓縮檔裡找不到 $name" }
  }

  $convert = @'
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
dest = Path(sys.argv[1])
pairs = [
    (Path(sys.argv[2]), dest / "NotoSansCJKtc-Regular.woff2"),
    (Path(sys.argv[3]), dest / "NotoSansCJKtc-Bold.woff2"),
]
for src, woff in pairs:
    font = TTFont(str(src), recalcBBoxes=False, recalcTimestamp=False)
    font.flavor = "woff2"
    font.save(str(woff))
    font.close()
    size = woff.stat().st_size
    if size < 1_000_000:
        raise SystemExit(f"{woff.name} 只有 {size} bytes，轉換可能失敗")
    print(f"  {woff.name}  {size/1024/1024:.1f} MB")
'@
  $pyFile = Join-Path $Tmp 'convert.py'
  # UTF-8 without BOM, so Python does not reject the first line.
  [System.IO.File]::WriteAllText($pyFile, $convert)
  Write-Host '轉成 woff2 …'
  & $Py $pyFile $Dest $got['NotoSansCJKtc-Regular.otf'] $got['NotoSansCJKtc-Bold.otf']
  if ($LASTEXITCODE -ne 0) { throw 'woff2 轉換失敗' }
} finally {
  Remove-Item -Recurse -Force $Tmp -ErrorAction SilentlyContinue
}

Write-Host "完成。這兩個 woff2 已在 .gitignore 裡，請不要 commit。"
Write-Host "授權：$Lic"

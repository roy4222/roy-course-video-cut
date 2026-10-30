# 取得 lemo-opuscar，並停在本專案用過的那個 commit。
# 上游：https://github.com/lemomo-ai/lemo-opuscar （MIT）
# 用法：powershell -NoProfile -ExecutionPolicy Bypass -File scripts\fetch_lemo_opuscar.ps1
$ErrorActionPreference = 'Stop'
$Pin = 'f17136060781a0068a7951245a3aa7835a7230de'
$Url = 'https://github.com/lemomo-ai/lemo-opuscar.git'
$Root = Split-Path -Parent $PSScriptRoot
if ($env:LEMO_OPUSCAR) { $Dest = $env:LEMO_OPUSCAR } else { $Dest = Join-Path $Root 'third_party\lemo-opuscar' }

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Dest) | Out-Null
if (-not (Test-Path (Join-Path $Dest '.git'))) {
  if (Test-Path $Dest) { Remove-Item -Recurse -Force $Dest }
  git init $Dest
  git -C $Dest remote add origin $Url
}
Write-Host "抓取 commit $Pin"
git -C $Dest fetch --depth 1 origin $Pin
if ($LASTEXITCODE -ne 0) { throw 'git fetch 失敗' }
git -C $Dest checkout --detach FETCH_HEAD
if ($LASTEXITCODE -ne 0) { throw 'git checkout 失敗' }

$Overlay = Join-Path $Root 'legacy\lemo_overlay\core\tts'
if (Test-Path $Overlay) {
  $Tts = Join-Path $Dest 'core\tts'
  New-Item -ItemType Directory -Force -Path $Tts | Out-Null
  Copy-Item -Force (Join-Path $Overlay '*.py') $Tts
  Write-Host '已把 legacy\lemo_overlay\core\tts\*.py 複製進 checkout（這是我們加的 TTS）。'
}

Write-Host ""
Write-Host "lemo-opuscar 在：$Dest"
Write-Host "舊管線若要叫它： `$env:LEMO_OPUSCAR = '$Dest'"
Write-Host '第一次使用請在該資料夾執行： npm ci'
Write-Host '授權全文（給 windows-kit\render 的修改版）：windows-kit\licenses\lemo-opuscar-MIT.txt'

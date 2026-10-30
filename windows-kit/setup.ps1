<#
 ml-video-kit setup for Windows 10/11. Non-interactive and idempotent: safe to run again at any time.
   powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 [-Cuda] [-NoModels] [-Python 3.11]
 What it does:
   1. uv (Python manager)            -> winget astral-sh.uv, fallback: official installer
   2. Python 3.11 venv in .venv       -> uv-managed Python (does NOT touch C:\Python38)
   3. Node.js 18+ and npm packages    -> winget OpenJS.NodeJS.LTS if node is missing
   4. Chromium headless shell         -> .browsers\ inside the kit folder
   5. ffmpeg / ffprobe check          -> winget Gyan.FFmpeg if missing (scoop ffmpeg is fine)
   6. Whisper "small" model           -> .cache\huggingface\ inside the kit folder; .env from .env.example
 -Cuda also installs cuBLAS/cuDNN wheels so faster-whisper can use the NVIDIA GPU (--whisper-device cuda).
#>
param([switch]$Cuda, [switch]$NoModels, [string]$Python = '3.11')
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Kit = $PSScriptRoot
Set-Location $Kit
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = '1'

function Say($m) { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Die($m) { Write-Host "`nERROR: $m" -ForegroundColor Red; exit 1 }
function Run($exe, [string[]]$argv) {
  & $exe @argv
  if ($LASTEXITCODE -ne 0) { Die "'$exe $($argv -join ' ')' failed (exit $LASTEXITCODE)" }
}
function Has($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Refresh-Path {
  $m = [Environment]::GetEnvironmentVariable('Path', 'Machine'); $u = [Environment]::GetEnvironmentVariable('Path', 'User')
  $env:Path = "$m;$u;$env:USERPROFILE\.local\bin;$env:USERPROFILE\scoop\shims;$env:LOCALAPPDATA\Microsoft\WinGet\Links"
}
function Winget-Install($id) {
  if (-not (Has winget)) { return $false }
  $old = $ErrorActionPreference; $ErrorActionPreference = 'Continue'   # winget writes progress to stderr
  try { & winget install --id $id -e --silent --accept-source-agreements --accept-package-agreements --disable-interactivity | Out-Host }
  finally { $ErrorActionPreference = $old }
  Refresh-Path
  return $true
}
Refresh-Path

# 1. uv ------------------------------------------------------------------
Say '1/6 uv (Python manager)'
if (-not (Has uv)) {
  Winget-Install 'astral-sh.uv' | Out-Null
  if (-not (Has uv)) {
    Write-Host 'winget did not provide uv; using the official installer'
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    Refresh-Path
  }
}
if (-not (Has uv)) { Die 'uv could not be installed. Install it manually: winget install astral-sh.uv' }
Run uv @('--version')

# 2. Python venv ---------------------------------------------------------
Say "2/6 Python $Python venv (.venv) + packages"
$Py = Join-Path $Kit '.venv\Scripts\python.exe'
if (Test-Path $Py) {
  $v = & $Py -c "import sys;print('%d.%d'%sys.version_info[:2])"
  if ($v -ne $Python) { Write-Host "existing .venv is Python $v (wanted $Python); recreating"; Remove-Item -Recurse -Force (Join-Path $Kit '.venv') }
}
if (-not (Test-Path $Py)) { Run uv @('venv', '--python', $Python, '.venv') }
Run uv @('pip', 'install', '--python', $Py, '-r', 'requirements.txt')
if ($Cuda) { Run uv @('pip', 'install', '--python', $Py, '-r', 'requirements-cuda.txt') }
Run $Py @('-c', 'import faster_whisper, soundfile, numpy, opencc; print(''python deps OK'')')

# 3. Node ----------------------------------------------------------------
Say '3/6 Node.js + playwright-core'
if (-not (Has node)) { Winget-Install 'OpenJS.NodeJS.LTS' | Out-Null }
if (-not (Has node)) { Die 'Node.js not found. Install it: winget install OpenJS.NodeJS.LTS  (then run setup again)' }
$nodeMajor = [int](& node -p "process.versions.node.split('.')[0]")
if ($nodeMajor -lt 18) { Die "Node.js $(& node -v) is too old; need 18+ (winget upgrade OpenJS.NodeJS.LTS)" }
Run npm @('install', '--no-audit', '--no-fund')

# 4. Chromium ------------------------------------------------------------
Say '4/6 Chromium headless shell into .browsers\'
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $Kit '.browsers'
Run node @('node_modules\playwright-core\cli.js', 'install', '--no-remove', 'chromium-headless-shell')

# 5. ffmpeg --------------------------------------------------------------
Say '5/6 ffmpeg / ffprobe'
if (-not ((Has ffmpeg) -and (Has ffprobe))) {
  Write-Host 'ffmpeg not found; installing with winget (Gyan.FFmpeg). Alternative: scoop install ffmpeg'
  Winget-Install 'Gyan.FFmpeg' | Out-Null
}
if (-not ((Has ffmpeg) -and (Has ffprobe))) { Die 'ffmpeg still not on PATH. Install: winget install Gyan.FFmpeg  or  scoop install ffmpeg, open a NEW PowerShell, run setup again.' }
& ffmpeg -hide_banner -version | Select-Object -First 1
$ErrorActionPreference = 'Continue'
$nv = (& ffmpeg -hide_banner -encoders 2>$null | Select-String 'h264_nvenc')
$ErrorActionPreference = 'Stop'
if ($nv -and (Has nvidia-smi)) {
  Write-Host 'NVIDIA GPU + h264_nvenc found: add --nvenc to make_episode for GPU encoding.' -ForegroundColor Green
} elseif (Has nvidia-smi) {
  Write-Host 'NVIDIA GPU found but this ffmpeg has no h264_nvenc (use the gyan.dev / scoop "ffmpeg" full build).'
}

# 6. Whisper model + .env ------------------------------------------------
Say '6/6 Whisper model + .env'
$env:HF_HOME = Join-Path $Kit '.cache\huggingface'
$env:HF_HUB_DISABLE_SYMLINKS_WARNING = '1'
if (-not $NoModels) {
  Run $Py @('-c', 'from faster_whisper import WhisperModel; WhisperModel(''small'', device=''cpu'', compute_type=''float32''); print(''whisper small cached'')')
}
if ($Cuda) {
  & $Py -c "import os;os.environ['KIT_WHISPER_DEVICE']='cuda';import sys;sys.path.insert(0,'.');from kit.whisper_util import model;model('small')"
}
if (-not (Test-Path (Join-Path $Kit '.env'))) {
  Copy-Item (Join-Path $Kit '.env.example') (Join-Path $Kit '.env')
  Write-Host 'created .env: open it and put your OPENROUTER_API_KEY there' -ForegroundColor Yellow
}
$wk = & $Py -c "import make_episode as m; print(m.auto_workers())"
Write-Host ''
Write-Host 'Setup finished.' -ForegroundColor Green
Write-Host "Auto render workers on this PC: $wk  (override with --workers N)"
Write-Host 'Smoke test (no API key needed, uses the bundled sample voice):'
Write-Host "  $Kit\make_episode.cmd episodes\sample"

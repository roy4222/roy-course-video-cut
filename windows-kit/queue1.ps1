# Serialize renders (NVENC session limit). Kit folder = this script, or ML_VIDEO_KIT.
$Kit = if ($env:ML_VIDEO_KIT) { $env:ML_VIDEO_KIT.TrimEnd('\') } else { $PSScriptRoot }
while (-not (Select-String -Path (Join-Path $Kit 'episodes\ep14.run.log') -Pattern '^EXIT' -Quiet)) { Start-Sleep 15 }
foreach ($e in $args) { & cmd.exe /c (Join-Path $Kit 'run_ep.cmd') $e }

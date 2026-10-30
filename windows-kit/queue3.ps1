# Wait for ep16 render and ep17 per-line TTS, then render ep17. One NVENC render at a time.
$Kit = if ($env:ML_VIDEO_KIT) { $env:ML_VIDEO_KIT.TrimEnd('\') } else { $PSScriptRoot }
function Done($f) { (Test-Path $f) -and (Select-String -Path $f -Pattern '^EXIT' -Quiet) }
$ep16 = Join-Path $Kit 'episodes\ep16.run.log'
$ep17tts = Join-Path $Kit 'episodes\ep17.tts.log'
while (-not ((Done $ep16) -and (Done $ep17tts))) { Start-Sleep 15 }
if (Select-String -Path $ep17tts -Pattern '^EXIT 0' -Quiet) { & cmd.exe /c (Join-Path $Kit 'run_ep.cmd') ep17 }

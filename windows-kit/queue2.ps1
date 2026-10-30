# Wait until <wait_ep>.run.log contains EXIT, then render the remaining episodes one by one.
param($wait)
$Kit = if ($env:ML_VIDEO_KIT) { $env:ML_VIDEO_KIT.TrimEnd('\') } else { $PSScriptRoot }
$log = Join-Path $Kit "episodes\$wait.run.log"
while (-not ((Test-Path $log) -and (Select-String -Path $log -Pattern '^EXIT' -Quiet))) { Start-Sleep 15 }
foreach ($e in $args) { & cmd.exe /c (Join-Path $Kit 'run_ep.cmd') $e }

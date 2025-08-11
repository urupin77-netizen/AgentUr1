# encoding: utf-8
Set-Location C:\AgentUr1
$latest = Get-ChildItem .\logs\uvicorn_*.log -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $latest) { $latest = Get-Item .\logs\diag_run.log -ErrorAction SilentlyContinue }
if (-not $latest) { Write-Error "Нет логов в .\logs"; exit 1 }
Write-Host ("==> Tail: " + $latest.FullName) -ForegroundColor Cyan
Get-Content $latest.FullName -Wait -Encoding UTF8

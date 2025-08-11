# C:\AgentUr1\scripts\tail_log.ps1
$log = Get-ChildItem "C:\AgentUr1\logs\pgpt_*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if (-not $log) { Write-Error "Лог не найден. Сначала запустите сервер через start_agent.ps1"; exit 1 }
Write-Host "Tailing: $($log.FullName)"
Get-Content -Path $log.FullName -Wait -Encoding UTF8

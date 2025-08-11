# C:\AgentUr1\scripts\debug_uvicorn.ps1
param(
  [string]$HostName = "0.0.0.0",
  [int]$Port = 8010
)
$ErrorActionPreference = "Stop"
$logs = "C:\AgentUr1\logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = Join-Path $logs "debug_uvicorn_$stamp.log"
Write-Host "Starting private_gpt.main:app on ${HostName}:${Port} (debug). Log: $logfile"
poetry run uvicorn private_gpt.main:app `
  --host $HostName --port $Port --log-level debug --reload *>> $logfile

# C:\AgentUr1\scripts\force_uvicorn.ps1
param(
  [string]$ServerHost = "0.0.0.0",
  [int]$ServerPort = 8010
)
$ErrorActionPreference = "Stop"
$logs = "C:\AgentUr1\logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = Join-Path $logs "force_uvicorn_$stamp.log"
Write-Host "Starting uvicorn private_gpt.main:app on $ServerHost`:$ServerPort. Log: $logfile"
poetry run uvicorn private_gpt.main:app --host $ServerHost --port $ServerPort --log-level info *>> $logfile

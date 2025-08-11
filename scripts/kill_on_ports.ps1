# C:\AgentUr1\scripts\kill_on_ports.ps1
param(
  [int[]]$Ports = @(8000,6333,6334,11434)
)

function Kill-ByPort {
  param([int]$Port)
  $lines = netstat -ano | Select-String ":$Port\s" | ForEach-Object { $_.ToString() }
  $pids = @()
  foreach ($l in $lines) {
    $parts = $l -split "\s+"
    if ($parts.Length -ge 5) { $pids += [int]$parts[-1] }
  }
  $pids = $pids | Select-Object -Unique
  foreach ($processId in $pids) {
    try {
      Write-Host "Killing PID $processId on port $Port"
      taskkill /PID $processId /F | Out-Null
    } catch { 
      Write-Warning "Failed to kill $processId" 
    }
  }
}

# Kill known names first (safety)
"qdrant","uvicorn","python","python3" | ForEach-Object {
  try { 
    taskkill /IM "$_.exe" /F | Out-Null 
  } catch { 
    Write-Host "No $_.exe process found" 
  }
}

$Ports | ForEach-Object { Kill-ByPort -Port $_ }
Write-Host "Done."

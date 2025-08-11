# C:\AgentUr1\scripts\reset_qdrant_data.ps1
param(
  [string]$RootDir = "C:\Users\aauru\AppData\Local\private_gpt"
)

# Ensure directory exists
New-Item -ItemType Directory -Path $RootDir -Force | Out-Null

# Take ownership & grant rights
takeown /F $RootDir /R /D Y | Out-Null
icacls $RootDir /grant "$($env:USERNAME):(OI)(CI)F" /T | Out-Null

# Optional: clean qdrant subfolder only
$qdrantDir = Join-Path $RootDir "qdrant"
if (Test-Path $qdrantDir) {
  Write-Host "Cleaning $qdrantDir ..."
  Remove-Item $qdrantDir -Recurse -Force
}
New-Item -ItemType Directory -Path $qdrantDir -Force | Out-Null

Write-Host "Prepared: $RootDir"

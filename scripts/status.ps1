# C:\AgentUr1\scripts\status.ps1
Write-Host "=== PrivateGPT Status Check ===" -ForegroundColor Green

# Проверка процессов Python
Write-Host "`nPython processes:" -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# Проверка процессов uvicorn
Write-Host "`nUvicorn processes:" -ForegroundColor Yellow
Get-Process uvicorn -ErrorAction SilentlyContinue | Select-Object Id, ProcessName, StartTime

# Проверка портов
Write-Host "`nPort 8000:" -ForegroundColor Yellow
netstat -ano | findstr ":8000" | Select-Object -First 3

Write-Host "`nPort 8010:" -ForegroundColor Yellow
netstat -ano | findstr ":8010" | Select-Object -First 3

# Проверка последних логов
Write-Host "`nLatest log files:" -ForegroundColor Yellow
Get-ChildItem "C:\AgentUr1\logs" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | Format-Table Name, LastWriteTime, Length -AutoSize

# encoding: utf-8
$ErrorActionPreference = "Stop"
chcp 65001 > $null
Set-Location C:\AgentUr1
New-Item -ItemType Directory -Path .\logs -Force | Out-Null

# Чистим хвосты
taskkill /IM uvicorn.exe /F 2>$null; taskkill /IM python.exe /F 2>$null

# Читаем порт из настроек; если не удалось — 8000
$port = (poetry run python -c "from private_gpt.settings.settings import settings; print(settings().server.port)" 2>$null)
if (-not $port) { $port = 8000 }

$log = ".\logs\uvicorn_$port.log"
Write-Host "==> Запуск API на порту $port; лог: $log" -ForegroundColor Cyan

# Открываем отдельное окно с сервером
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","cd C:\AgentUr1; poetry run uvicorn private_gpt.main:app --host 0.0.0.0 --port $port --log-level debug *>> $log" -WindowStyle Normal

# Небольшая пауза и быстрый health-пинг
Start-Sleep -Seconds 3
try {
  (Invoke-WebRequest -Uri ("http://127.0.0.1:{0}/health" -f $port) -UseBasicParsing -TimeoutSec 5).StatusCode
} catch {
  Write-Warning "Health пока не отвечает — посмотри хвост лога: powershell -NoProfile -Command Get-Content $log -Wait -Encoding UTF8"
}

# C:\AgentUr1\scripts\run_app.ps1
param(
  [string]$Entry="private_gpt.main:app",   # <--- ВАРИАНТ 1: FastAPI: модуль:объект
  [int]$Port=8000,
  [string]$Host="0.0.0.0"
)
$ErrorActionPreference = "Stop"

# Создаём папку для логов
$logs = "C:\AgentUr1\logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null

# Генерируем имя лог-файла с временной меткой
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = Join-Path $logs "app_$stamp.log"

Write-Host "=== ЗАПУСК ПРИЛОЖЕНИЯ AGENTUR1 ===" -ForegroundColor Green
Write-Host "Entry point: $Entry" -ForegroundColor Cyan
Write-Host "Host: $Host" -ForegroundColor Cyan
Write-Host "Port: $Port" -ForegroundColor Cyan
Write-Host "Лог-файл: $logfile" -ForegroundColor Cyan
Write-Host ""

# Проверяем, что порт свободен
$portCheck = netstat -ano | findstr ":$Port\s"
if ($portCheck) {
    Write-Host "⚠️ Порт $Port занят! Снимаем блокировки..." -ForegroundColor Yellow
    & "C:\AgentUr1\scripts\kill_on_ports.ps1" -Ports @($Port)
    Start-Sleep -Seconds 2
}

# ВАРИАНТЫ запуска (раскомментируйте нужный, остальные закомментируйте):

# 1) Uvicorn c FastAPI (рекомендуется для вашего случая):
Write-Host "Запуск через uvicorn..." -ForegroundColor Green
poetry run uvicorn $Entry --host $Host --port $Port --reload *>> $logfile

# 2) Если у вас свой launcher (пример):
# Write-Host "Запуск через модуль..." -ForegroundColor Green
# poetry run python -m private_gpt.main *>> $logfile

# 3) Если у вас Typer/Click CLI:
# Write-Host "Запуск через CLI..." -ForegroundColor Green
# poetry run python -m private_gpt.cli serve --host $Host --port $Port *>> $logfile

# 4) Прямой запуск Python файла:
# Write-Host "Прямой запуск Python..." -ForegroundColor Green
# poetry run python private_gpt/main.py *>> $logfile

Write-Host ""
Write-Host "Приложение запущено! Логи сохраняются в: $logfile" -ForegroundColor Green
Write-Host "Для просмотра логов в реальном времени используйте:" -ForegroundColor Cyan
Write-Host "Get-Content $logfile -Wait" -ForegroundColor White


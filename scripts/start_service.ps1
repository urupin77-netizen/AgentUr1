# C:\AgentUr1\scripts\start_service.ps1
# Запуск в режиме без Qdrant (рекомендуется для стабилизации)

Write-Host "Starting AgentUr1 service..." -ForegroundColor Green

# Переходим в рабочую директорию
Set-Location "C:\AgentUr1"

# Снятие блокировок портов
Write-Host "Clearing port locks..." -ForegroundColor Yellow
if (Test-Path "scripts\kill_on_ports.ps1") {
    & "scripts\kill_on_ports.ps1"
}

# Проверка YAML
Write-Host "Validating YAML configuration..." -ForegroundColor Yellow
poetry run python tools\validate_yaml.py settings.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "YAML validation passed!" -ForegroundColor Green
    
    # Запуск FastAPI сервиса через универсальный скрипт
    Write-Host "Starting FastAPI service..." -ForegroundColor Green
    Write-Host "Make sure Ollama is running (ollama serve) in another terminal" -ForegroundColor Cyan
    
    # Используем универсальный скрипт запуска с логированием
    & "scripts\run_app.ps1" -Entry "private_gpt.main:app" -Port 8000 -Host "0.0.0.0"
} else {
    Write-Host "YAML validation failed! Please fix configuration issues." -ForegroundColor Red
    exit 1
}

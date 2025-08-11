# C:\AgentUr1\scripts\smoke_test.ps1
# Дымовой тест для диагностики сети и фаервола

Write-Host "=== 🔥 ДЫМОВОЙ ТЕСТ СЕТИ ===" -ForegroundColor Green
Write-Host "Назначение: Проверка доступности порта 8000 и сетевых настроек" -ForegroundColor Cyan
Write-Host ""

# Переходим в рабочую директорию
Set-Location "C:\AgentUr1"

# 1. Очистка портов
Write-Host "1. Очистка портов..." -ForegroundColor Yellow
if (Test-Path "scripts\kill_on_ports.ps1") {
    & "scripts\kill_on_ports.ps1"
    Start-Sleep -Seconds 2
} else {
    Write-Host "⚠️ Скрипт kill_on_ports.ps1 не найден" -ForegroundColor Yellow
}

# 2. Проверка свободных портов
Write-Host "2. Проверка свободных портов..." -ForegroundColor Yellow
$ports = @(8000, 6333, 11434)
foreach ($port in $ports) {
    $check = netstat -ano | findstr ":$port\s"
    if ($check) {
        Write-Host "❌ Порт $port занят:" -ForegroundColor Red
        Write-Host $check -ForegroundColor Red
    } else {
        Write-Host "✅ Порт $port свободен" -ForegroundColor Green
    }
}

Write-Host ""

# 3. Проверка зависимостей
Write-Host "3. Проверка зависимостей..." -ForegroundColor Yellow
try {
    $fastapiCheck = poetry run python -c "import fastapi, uvicorn; print('FastAPI + Uvicorn доступны')" 2>&1
    Write-Host "✅ FastAPI + Uvicorn установлены" -ForegroundColor Green
} catch {
    Write-Host "❌ FastAPI + Uvicorn не установлены" -ForegroundColor Red
    Write-Host "Установите: poetry add fastapi uvicorn" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# 4. Запуск дымового сервера
Write-Host "4. Запуск дымового сервера..." -ForegroundColor Yellow
Write-Host "🔥 Запускаем диагностический сервер на порту 8000..." -ForegroundColor Green
Write-Host "📡 В другом терминале проверьте:" -ForegroundColor Cyan
Write-Host "   curl http://localhost:8000/health" -ForegroundColor White
Write-Host "   curl http://localhost:8000/" -ForegroundColor White
Write-Host "   curl http://localhost:8000/ping" -ForegroundColor White
Write-Host ""
Write-Host "💡 Для остановки сервера нажмите Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Запуск дымового сервера
try {
    poetry run python tools\smoke_health.py
} catch {
    Write-Host "❌ Ошибка запуска дымового сервера:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}


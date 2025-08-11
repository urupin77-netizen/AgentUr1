# C:\AgentUr1\scripts\run_pgpt.ps1
# Скрипт для запуска PrivateGPT с логированием

$ErrorActionPreference = "Stop"

# Создаем папку для логов
$logs = "C:\AgentUr1\logs"
New-Item -ItemType Directory -Path $logs -Force | Out-Null

# Генерируем имя файла лога с временной меткой
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logfile = Join-Path $logs "pgpt_$stamp.log"

Write-Host "=== Запуск PrivateGPT ===" -ForegroundColor Green
Write-Host "Лог файл: $logfile" -ForegroundColor Yellow
Write-Host "Текущая директория: $(Get-Location)" -ForegroundColor Yellow

# Проверяем, что poetry доступен
try {
    $poetryVersion = poetry --version
    Write-Host "Poetry версия: $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "Ошибка: Poetry не найден!" -ForegroundColor Red
    Write-Host "Убедитесь, что Poetry установлен и доступен в PATH" -ForegroundColor Red
    exit 1
}

# Проверяем зависимости
Write-Host "`nПроверка зависимостей..." -ForegroundColor Yellow
try {
    poetry install --no-dev
    Write-Host "Зависимости установлены" -ForegroundColor Green
} catch {
    Write-Host "Ошибка при установке зависимостей: $_" -ForegroundColor Red
    exit 1
}

# Запускаем PrivateGPT через __main__.py
Write-Host "`nЗапуск PrivateGPT..." -ForegroundColor Yellow
Write-Host "Команда: poetry run python ." -ForegroundColor Cyan

try {
    # Запускаем с перенаправлением вывода в лог файл
    poetry run python . *>> $logfile 2>&1
} catch {
    Write-Host "Ошибка при запуске: $_" -ForegroundColor Red
    Write-Host "Проверьте лог файл: $logfile" -ForegroundColor Yellow
    exit 1
}

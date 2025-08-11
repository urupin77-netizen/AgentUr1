# C:\AgentUr1\scripts\view_logs.ps1
# Просмотр логов приложения

param(
    [int]$Lines = 50,           # Количество последних строк
    [switch]$Follow,            # Следить за логами в реальном времени
    [string]$LogFile = ""       # Конкретный лог-файл (если не указан - последний)
)

$logsDir = "C:\AgentUr1\logs"

if (-not (Test-Path $logsDir)) {
    Write-Host "❌ Папка логов не найдена: $logsDir" -ForegroundColor Red
    exit 1
}

# Если лог-файл не указан, берём последний
if (-not $LogFile) {
    $logFiles = Get-ChildItem -Path $logsDir -Filter "app_*.log" | Sort-Object LastWriteTime -Descending
    if ($logFiles.Count -eq 0) {
        Write-Host "❌ Лог-файлы не найдены в: $logsDir" -ForegroundColor Red
        exit 1
    }
    $LogFile = $logFiles[0].FullName
    Write-Host "📋 Используем последний лог-файл: $(Split-Path $LogFile -Leaf)" -ForegroundColor Cyan
}

if (-not (Test-Path $LogFile)) {
    Write-Host "❌ Лог-файл не найден: $LogFile" -ForegroundColor Red
    exit 1
}

Write-Host "=== ПРОСМОТР ЛОГОВ ===" -ForegroundColor Green
Write-Host "Файл: $LogFile" -ForegroundColor Cyan
Write-Host "Размер: $((Get-Item $LogFile).Length) байт" -ForegroundColor Cyan
Write-Host ""

if ($Follow) {
    Write-Host "🔍 Следим за логами в реальном времени (Ctrl+C для выхода)..." -ForegroundColor Yellow
    Get-Content $LogFile -Wait
} else {
    Write-Host "📖 Последние $Lines строк лога:" -ForegroundColor Yellow
    Get-Content $LogFile -Tail $Lines
}

Write-Host ""
Write-Host "💡 Для просмотра в реальном времени используйте:" -ForegroundColor Cyan
Write-Host ".\scripts\view_logs.ps1 -Follow" -ForegroundColor White
Write-Host "💡 Для просмотра конкретного файла:" -ForegroundColor Cyan
Write-Host ".\scripts\view_logs.ps1 -LogFile 'logs\app_20241201_120000.log'" -ForegroundColor White


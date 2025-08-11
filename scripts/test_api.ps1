# C:\AgentUr1\scripts\test_api.ps1
# Тестирование API эндпойнтов дымового сервера

param(
    [string]$Host = "localhost",
    [int]$Port = 8000
)

Write-Host "=== 🧪 ТЕСТИРОВАНИЕ API ===" -ForegroundColor Green
Write-Host "Хост: $Host" -ForegroundColor Cyan
Write-Host "Порт: $Port" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://$Host`:$Port"

# Функция для тестирования эндпойнта
function Test-Endpoint {
    param([string]$Path, [string]$Description)
    
    $url = "$baseUrl$Path"
    Write-Host "🔍 Тестируем: $Description" -ForegroundColor Yellow
    Write-Host "   URL: $url" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Успешно (HTTP $($response.StatusCode))" -ForegroundColor Green
            try {
                $content = $response.Content | ConvertFrom-Json
                Write-Host "   📄 Ответ: $($content | ConvertTo-Json -Compress)" -ForegroundColor Gray
            } catch {
                Write-Host "   📄 Ответ: $($response.Content)" -ForegroundColor Gray
            }
        } else {
            Write-Host "   ⚠️ Неожиданный статус: HTTP $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    }
    Write-Host ""
}

# Проверяем доступность сервера
Write-Host "1. Проверка доступности сервера..." -ForegroundColor Cyan
try {
    $ping = Invoke-WebRequest -Uri "$baseUrl/ping" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Сервер доступен на $baseUrl" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "❌ Сервер недоступен на $baseUrl" -ForegroundColor Red
    Write-Host "Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Убедитесь, что дымовой сервер запущен:" -ForegroundColor Cyan
    Write-Host "   .\scripts\smoke_test.ps1" -ForegroundColor White
    exit 1
}

# Тестируем все эндпойнты
Write-Host "2. Тестирование эндпойнтов..." -ForegroundColor Cyan

Test-Endpoint -Path "/" -Description "Корневой эндпойнт"
Test-Endpoint -Path "/health" -Description "Health check"
Test-Endpoint -Path "/ping" -Description "Ping эндпойнт"

# Проверяем несуществующий эндпойнт
Write-Host "3. Тестирование несуществующего эндпойнта..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/nonexistent" -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "⚠️ Неожиданно: несуществующий эндпойнт вернул HTTP $($response.StatusCode)" -ForegroundColor Yellow
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "✅ Корректно: несуществующий эндпойнт вернул 404" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== 🎯 РЕЗУЛЬТАТ ТЕСТА ===" -ForegroundColor Green
Write-Host "Если все тесты прошли успешно, порт 8000 доступен и фаервол не блокирует" -ForegroundColor Cyan
Write-Host "Теперь можно запускать основное приложение:" -ForegroundColor White
Write-Host "   .\scripts\start_service.ps1" -ForegroundColor White


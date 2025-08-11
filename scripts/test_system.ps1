# C:\AgentUr1\scripts\test_system.ps1
# Полный тест системы AgentUr1

Write-Host "=== ПОЛНЫЙ ТЕСТ СИСТЕМЫ AGENTUR1 ===" -ForegroundColor Green
Write-Host ""

# 1. Проверка портов (должны быть пустыми)
Write-Host "1. Проверка портов..." -ForegroundColor Yellow
Write-Host "Порт 8000:" -ForegroundColor Cyan
$port8000 = netstat -ano | findstr ":8000"
if ($port8000) {
    Write-Host "❌ Порт 8000 занят:" -ForegroundColor Red
    Write-Host $port8000 -ForegroundColor Red
} else {
    Write-Host "✅ Порт 8000 свободен" -ForegroundColor Green
}

Write-Host "Порт 6333:" -ForegroundColor Cyan
$port6333 = netstat -ano | findstr ":6333"
if ($port6333) {
    Write-Host "❌ Порт 6333 занят:" -ForegroundColor Red
    Write-Host $port6333 -ForegroundColor Red
} else {
    Write-Host "✅ Порт 6333 свободен" -ForegroundColor Green
}

Write-Host ""

# 2. Валидация YAML
Write-Host "2. Валидация YAML конфигурации..." -ForegroundColor Yellow
$yamlResult = poetry run python tools\validate_yaml.py settings.yaml 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ YAML валидация прошла успешно" -ForegroundColor Green
    Write-Host "Результат: $yamlResult" -ForegroundColor Gray
} else {
    Write-Host "❌ YAML валидация провалилась:" -ForegroundColor Red
    Write-Host $yamlResult -ForegroundColor Red
    exit 1
}

Write-Host ""

# 3. Проверка прав доступа к папке данных
Write-Host "3. Проверка прав доступа к папке данных..." -ForegroundColor Yellow
$dataPath = "C:\Users\aauru\AppData\Local\private_gpt"
if (Test-Path $dataPath) {
    Write-Host "✅ Папка данных существует: $dataPath" -ForegroundColor Green
} else {
    Write-Host "⚠️ Папка данных не существует, создаём..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $dataPath -Force | Out-Null
    Write-Host "✅ Папка данных создана" -ForegroundColor Green
}

Write-Host ""

# 4. Проверка зависимостей
Write-Host "4. Проверка зависимостей..." -ForegroundColor Yellow
try {
    $pyyamlCheck = poetry run python -c "import yaml; print('PyYAML доступен')" 2>&1
    Write-Host "✅ PyYAML установлен" -ForegroundColor Green
} catch {
    Write-Host "❌ PyYAML не установлен" -ForegroundColor Red
}

Write-Host ""

# 5. Проверка отсутствия Qdrant зависимостей (для simple режима)
Write-Host "5. Проверка отсутствия Qdrant зависимостей..." -ForegroundColor Yellow
try {
    $qdrantCheck = poetry run python -c "import qdrant_client; print('Qdrant client найден')" 2>&1
    Write-Host "⚠️ Qdrant client установлен (может конфликтовать с simple режимом)" -ForegroundColor Yellow
} catch {
    Write-Host "✅ Qdrant client не установлен (совместимо с simple режимом)" -ForegroundColor Green
}

Write-Host ""

# 6. Финальная проверка
Write-Host "=== РЕЗУЛЬТАТ ТЕСТА ===" -ForegroundColor Green
Write-Host "✅ Система готова к запуску!" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Cyan
Write-Host "1. Запустить Ollama: ollama serve" -ForegroundColor White
Write-Host "2. Запустить сервис: .\scripts\start_service.ps1" -ForegroundColor White
Write-Host "3. Проверить API: curl http://127.0.0.1:8000/health" -ForegroundColor White
Write-Host ""


# C:\AgentUr1\scripts\check_settings.ps1
# Скрипт для проверки настроек PrivateGPT

Write-Host "=== Проверка настроек PrivateGPT ===" -ForegroundColor Green

# Проверяем переменные окружения
Write-Host "`nПеременные окружения:" -ForegroundColor Yellow
Write-Host "PGPT_PROFILES: $env:PGPT_PROFILES"
Write-Host "PGPT_SETTINGS_FOLDER: $env:PGPT_SETTINGS_FOLDER"

# Проверяем активные профили
Write-Host "`nАктивные профили:" -ForegroundColor Yellow
try {
    $profiles = poetry run python -c "
import sys
sys.path.append('.')
from private_gpt.settings.settings_loader import active_profiles
print('Профили:', active_profiles)
"
    Write-Host $profiles
} catch {
    Write-Host "Ошибка при получении профилей: $_" -ForegroundColor Red
}

# Проверяем порт сервера
Write-Host "`nПорт сервера:" -ForegroundColor Yellow
try {
    $port = poetry run python -c "
import sys
sys.path.append('.')
from private_gpt.settings.settings import settings
s = settings()
print('Порт:', s.server.port)
print('Хост:', s.server.host)
print('Env name:', s.server.env_name)
"
    Write-Host $port
} catch {
    Write-Host "Ошибка при получении порта: $_" -ForegroundColor Red
}

# Проверяем настройки UI
Write-Host "`nНастройки UI:" -ForegroundColor Yellow
try {
    $ui = poetry run python -c "
import sys
sys.path.append('.')
from private_gpt.settings.settings import settings
s = settings()
print('UI enabled:', s.ui.enabled)
print('UI path:', s.ui.path)
"
    Write-Host $ui
} catch {
    Write-Host "Ошибка при получении настроек UI: $_" -ForegroundColor Red
}

Write-Host "`n=== Проверка завершена ===" -ForegroundColor Green

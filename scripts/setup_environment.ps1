# C:\AgentUr1\scripts\setup_environment.ps1
# Подготовка окружения (один раз)

Write-Host "Setting up AgentUr1 environment..." -ForegroundColor Green

# Переходим в рабочую директорию
Set-Location "C:\AgentUr1"

# Установка зависимостей на YAML
Write-Host "Installing PyYAML dependency..." -ForegroundColor Yellow
poetry add pyyaml

# Для режима с Qdrant (раскомментировать если нужен):
# Write-Host "Installing Qdrant client..." -ForegroundColor Yellow
# poetry add qdrant-client

Write-Host "Environment setup completed!" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Validate YAML: poetry run python tools\validate_yaml.py settings.yaml" -ForegroundColor White
Write-Host "2. Start service: poetry run uvicorn private_gpt.main:app --host 0.0.0.0 --port 8000" -ForegroundColor White


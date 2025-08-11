# AgentUr1 Configuration Guide

## Overview
This guide covers the configuration setup for AgentUr1, including YAML validation, configuration adaptation, and optional Qdrant setup.

## Files Structure

### Core Configuration
- `settings.yaml` - Main configuration (simple vector store, no Qdrant)
- `settings.qdrant.yaml` - Optional Qdrant configuration
- `tools/validate_yaml.py` - YAML syntax and structure validator
- `tools/config_adapter.py` - Legacy key compatibility adapter

### Optional Qdrant Support
- `tools/init_qdrant.py` - Qdrant collection initialization
- `scripts/setup_environment.ps1` - Environment setup script
- `scripts/start_service.ps1` - Service startup script

### Application Launch & Logging
- `scripts/run_app.ps1` - Universal application launcher with logging
- `scripts/view_logs.ps1` - Log viewer utility
- `scripts/kill_on_ports.ps1` - Port cleanup utility

### Network Diagnostics
- `tools/smoke_health.py` - Simple diagnostic server for network testing
- `scripts/smoke_test.ps1` - Smoke test launcher
- `scripts/test_api.ps1` - API endpoint testing utility

## Quick Start (Recommended: Simple Mode)

### 1. Environment Setup
```powershell
cd C:\AgentUr1
powershell -ExecutionPolicy Bypass -File scripts\setup_environment.ps1
```

### 2. Validate Configuration
```powershell
poetry run python tools\validate_yaml.py settings.yaml
```
Expected output: `PARSED OK.`

### 3. Start Service
```powershell
# Make sure Ollama is running in another terminal:
# ollama serve

# Start the service:
powershell -ExecutionPolicy Bypass -File scripts\start_service.ps1
```

## Network Diagnostics (Smoke Test)

If your main application fails to start, use the smoke test to verify network connectivity and firewall settings.

### 1. Run Smoke Test
```powershell
# Launch diagnostic server on port 8000
powershell -ExecutionPolicy Bypass -File scripts\smoke_test.ps1
```

### 2. Test API Endpoints
```powershell
# In another terminal, test the endpoints:
powershell -ExecutionPolicy Bypass -File scripts\test_api.ps1

# Or manually with curl:
curl http://localhost:8000/health
curl http://localhost:8000/
curl http://localhost:8000/ping
```

### 3. Expected Results
- **Port 8000 accessible**: Smoke server starts without errors
- **Health endpoint**: Returns `{"status": "ok"}`
- **Root endpoint**: Returns server status message
- **Ping endpoint**: Returns `{"pong": "ok"}`

### 4. Troubleshooting Network Issues
If smoke test fails:
1. **Check Windows Firewall**: Allow Python/uvicorn through firewall
2. **Check antivirus**: Temporarily disable to test
3. **Check port conflicts**: Use `scripts\kill_on_ports.ps1`
4. **Check network adapters**: Ensure localhost binding works

## Application Launch Options

### Universal Launcher (`run_app.ps1`)
```powershell
# Basic usage (FastAPI with uvicorn)
.\scripts\run_app.ps1

# Custom entry point
.\scripts\run_app.ps1 -Entry "myapp.main:app" -Port 8080

# Custom host
.\scripts\run_app.ps1 -Host "127.0.0.1"
```

### Launch Variants
The `run_app.ps1` script supports multiple launch methods:

1. **FastAPI + Uvicorn** (recommended):
   ```powershell
   poetry run uvicorn private_gpt.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Python module**:
   ```powershell
   poetry run python -m private_gpt.main
   ```

3. **CLI application**:
   ```powershell
   poetry run python -m private_gpt.cli serve --host 0.0.0.0 --port 8000
   ```

4. **Direct Python file**:
   ```powershell
   poetry run python private_gpt/main.py
   ```

### Logging
- Logs are automatically saved to `logs/app_YYYYMMDD_HHMMSS.log`
- Use `.\scripts\view_logs.ps1` to view logs
- Real-time log monitoring: `.\scripts\view_logs.ps1 -Follow`

## Configuration Details

### Main Settings (`settings.yaml`)
- **Server**: Host 0.0.0.0, Port 8000
- **UI**: Enabled with root path "/"
- **Data**: Local storage in AppData
- **Vector Store**: Simple (no external database)
- **LLM**: Ollama integration

### Key Features
- Single profile configuration
- UTF-8 encoding
- Legacy key compatibility
- No Qdrant dependency

## Advanced: Qdrant Mode

### 1. Install Qdrant Client
```powershell
poetry add qdrant-client
```

### 2. Initialize Qdrant Collection
```powershell
$env:QDRANT_URL="http://127.0.0.1:6333"
$env:QDRANT_COLLECTION="documents"
$env:QDRANT_VECTOR_SIZE="768"
$env:QDRANT_DISTANCE="Cosine"
poetry run python tools\init_qdrant.py
```

### 3. Use Qdrant Configuration
```powershell
# Copy Qdrant settings
copy settings.qdrant.yaml settings.yaml

# Validate and start
poetry run python tools\validate_yaml.py settings.yaml
```

## Configuration Adapter

The `config_adapter.py` provides backward compatibility:
- Automatically sets `rag.vector_store: "simple"` if missing
- Merges profile configurations
- Fixes legacy collection names
- Handles missing keys gracefully

## Troubleshooting

### Common Issues
1. **YAML Syntax Error**: Check indentation (use spaces, not tabs)
2. **Missing Keys**: Verify all required top-level keys are present
3. **Port Conflicts**: Use `scripts\kill_on_ports.ps1` to clear ports
4. **Ollama Connection**: Ensure Ollama is running on port 11434
5. **Network/Firewall**: Use smoke test to verify connectivity

### Validation Commands
```powershell
# Basic validation
poetry run python tools\validate_yaml.py settings.yaml

# Check specific file
poetry run python tools\validate_yaml.py settings.qdrant.yaml

# Debug configuration loading
poetry run python -c "import yaml; print(yaml.safe_load(open('settings.yaml')))"
```

### Log Analysis
```powershell
# View latest logs
.\scripts\view_logs.ps1

# Follow logs in real-time
.\scripts\view_logs.ps1 -Follow

# View specific log file
.\scripts\view_logs.ps1 -LogFile "logs\app_20241201_120000.log"
```

### Network Diagnostics
```powershell
# Run smoke test
.\scripts\smoke_test.ps1

# Test API endpoints
.\scripts\test_api.ps1

# Manual curl tests
curl http://localhost:8000/health
curl http://localhost:8000/ping
```

## Exit Codes

- `0`: Success
- `1`: YAML syntax error
- `2`: Usage error or file not found
- `3`: Missing required keys
- `4`: Profile reference error

## Next Steps

1. Test the configuration with the validator
2. Run smoke test to verify network connectivity
3. Start the service in simple mode
4. Verify UI accessibility at http://localhost:8000
5. Test document ingestion and RAG functionality
6. Consider Qdrant mode for production use if needed

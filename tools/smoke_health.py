# C:\AgentUr1\tools\smoke_health.py
from __future__ import annotations
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    """Простой health-check для диагностики порта 8000."""
    return {"status": "ok"}

@app.get("/")
def root():
    """Корневой эндпойнт для проверки доступности."""
    return {"message": "Smoke test server is running", "status": "healthy"}

@app.get("/ping")
def ping():
    """Простой ping для быстрой проверки."""
    return {"pong": "ok"}

if __name__ == "__main__":
    print("🔥 Запуск дымового сервера на порту 8000...")
    print("📡 Проверьте доступность:")
    print("   - http://localhost:8000/")
    print("   - http://localhost:8000/health")
    print("   - http://localhost:8000/ping")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)


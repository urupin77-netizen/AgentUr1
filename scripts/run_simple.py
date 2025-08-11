#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для запуска PrivateGPT
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Запускает PrivateGPT"""
    print("=== Запуск PrivateGPT ===")
    
    try:
        # Проверяем настройки
        from private_gpt.settings.settings import settings
        s = settings()
        print(f"Порт сервера: {s.server.port}")
        print(f"Хост сервера: {s.server.host}")
        print(f"UI включен: {s.ui.enabled}")
        
        # Запускаем приложение
        from private_gpt.__main__ import main as pgpt_main
        print("Запуск PrivateGPT...")
        pgpt_main()
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

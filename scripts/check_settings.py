#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для проверки настроек PrivateGPT
"""

import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_settings():
    """Проверяет настройки PrivateGPT"""
    print("=== Проверка настроек PrivateGPT ===")
    
    # Проверяем переменные окружения
    print("\nПеременные окружения:")
    print(f"PGPT_PROFILES: {os.environ.get('PGPT_PROFILES', 'не установлена')}")
    print(f"PGPT_SETTINGS_FOLDER: {os.environ.get('PGPT_SETTINGS_FOLDER', 'не установлена')}")
    
    try:
        # Проверяем активные профили
        from private_gpt.settings.settings_loader import active_profiles
        print(f"\nАктивные профили: {active_profiles}")
        
        # Проверяем порт сервера
        from private_gpt.settings.settings import settings
        s = settings()
        print(f"\nПорт сервера: {s.server.port}")
        print(f"Хост сервера: {s.server.host}")
        print(f"Имя окружения: {s.server.env_name}")
        
        # Проверяем настройки UI
        print(f"\nНастройки UI:")
        print(f"  UI включен: {s.ui.enabled}")
        print(f"  Путь UI: {s.ui.path}")
        
        # Проверяем настройки LLM
        print(f"\nНастройки LLM:")
        print(f"  Режим: {s.llm.mode}")
        
        # Проверяем настройки embedding
        print(f"\nНастройки Embedding:")
        print(f"  Режим: {s.embedding.mode}")
        
        # Проверяем настройки vectorstore
        print(f"\nНастройки Vectorstore:")
        print(f"  База данных: {s.vectorstore.database}")
        
        # Проверяем настройки nodestore
        print(f"\nНастройки Nodestore:")
        print(f"  База данных: {s.nodestore.database}")
        
    except Exception as e:
        print(f"\nОшибка при получении настроек: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Проверка завершена ===")

if __name__ == "__main__":
    check_settings()

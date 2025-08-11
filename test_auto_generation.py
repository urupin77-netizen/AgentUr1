#!/usr/bin/env python3
"""Тест автогенерации гипотез."""

import requests
import json
import time

def test_auto_generation():
    """Тестирует автогенерацию гипотез."""
    base_url = "http://localhost:8000"
    
    print("=== ТЕСТ АВТОГЕНЕРАЦИИ ГИПОТЕЗ ===")
    print()
    
    # Шаг 1: Проверяем текущие гипотезы
    print("1. Проверяем текущие гипотезы...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=10")
        if response.status_code == 200:
            hypotheses = response.json()
            print(f"   ✅ Найдено гипотез: {len(hypotheses)}")
        else:
            print(f"   ❌ Ошибка получения гипотез: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # Шаг 2: Отправляем простой чат для срабатывания автогенерации
    print("\n2. Отправляем тестовый чат...")
    chat_payload = {
        "messages": [
            {"role": "user", "content": "Расскажи мне что-нибудь интересное о космосе"}
        ],
        "use_context": False,
        "include_sources": False,
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=chat_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Чат завершен успешно")
            print(f"   📝 Ответ: {result.get('response', 'Нет ответа')[:100]}...")
        else:
            print(f"   ❌ Ошибка чата: {response.status_code}")
            print(f"   📄 Ответ: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
        return
    
    # Шаг 3: Ждем немного для обработки
    print("\n3. Ждем обработки (3 секунды)...")
    time.sleep(3)
    
    # Шаг 4: Проверяем, появились ли новые гипотезы
    print("\n4. Проверяем новые гипотезы...")
    try:
        response = requests.get(f"{base_url}/v1/hypothesis/list?limit=10")
        if response.status_code == 200:
            hypotheses = response.json()
            auto_hypotheses = [h for h in hypotheses if "auto" in h.get('tags', [])]
            
            print(f"   📊 Всего гипотез: {len(hypotheses)}")
            print(f"   🔄 Автогенерированных: {len(auto_hypotheses)}")
            
            if auto_hypotheses:
                print("\n   📋 Автогенерированные гипотезы:")
                for i, hyp in enumerate(auto_hypotheses, 1):
                    print(f"      {i}. {hyp.get('title', 'Без названия')}")
                    print(f"         ID: {hyp.get('id')}")
                    print(f"         Теги: {hyp.get('tags', [])}")
                    print(f"         Уверенность: {hyp.get('confidence', 0)}")
                    print(f"         Приоритет: {hyp.get('priority', 3)}")
                    print()
            else:
                print("   ⚠️ Автогенерированных гипотез не найдено")
                
        else:
            print(f"   ❌ Ошибка получения гипотез: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # Шаг 5: Тестируем ручную генерацию гипотезы
    print("\n5. Тестируем ручную генерацию гипотезы...")
    manual_payload = {
        "last_user_message": "Тестовое сообщение для проверки",
        "assistant_response": "Тестовый ответ ассистента",
        "reflection": None,
        "top_memory_limit": 3,
        "tags": ["test", "manual"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/hypothesis/generate",
            json=manual_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Гипотеза сгенерирована вручную")
            print(f"   📝 Название: {result.get('title', 'Без названия')}")
            print(f"   🏷️ Теги: {result.get('tags', [])}")
        else:
            print(f"   ❌ Ошибка генерации: {response.status_code}")
            print(f"   📄 Ответ: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    print("\n=== ТЕСТ ЗАВЕРШЕН ===")

if __name__ == "__main__":
    test_auto_generation()

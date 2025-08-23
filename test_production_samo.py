#!/usr/bin/env python3
"""
Прямой тест SAMO API с продакшн сервера через его API
"""

import requests
import json

def test_production_samo():
    """Тест SAMO API через продакшн сервер"""
    
    print("🚀 ТЕСТ SAMO API С ПРОДАКШН СЕРВЕРА")
    print("=" * 40)
    
    production_url = "http://46.250.234.89:5000"
    
    # Сначала проверим IP продакшн сервера
    try:
        server_response = requests.get(f"{production_url}/api/diagnostics/server", timeout=15)
        if server_response.status_code == 200:
            server_data = server_response.json()
            server_ip = server_data.get("external_ip", "Unknown")
            print(f"📍 IP продакшн сервера: {server_ip}")
        else:
            print("❌ Не удалось получить IP сервера")
            return
    except Exception as e:
        print(f"❌ Ошибка подключения к продакшн серверу: {e}")
        return
    
    # Тестируем SAMO API через продакшн сервер
    try:
        print("\n🧪 Тестирование SAMO API через продакшн...")
        
        # Используем endpoint продакшн сервера для выполнения curl
        curl_response = requests.post(
            f"{production_url}/api/samo/execute-curl",
            json={"method": "SearchTour_CURRENCIES", "params": ""},
            timeout=30
        )
        
        if curl_response.status_code == 200:
            curl_data = curl_response.json()
            
            print(f"📊 Результат curl теста:")
            print(f"   Status Code: {curl_data.get('status_code', 'N/A')}")
            print(f"   Command: {curl_data.get('command', 'N/A')}")
            
            response_text = curl_data.get('response', '')[:200]
            print(f"   Response (first 200 chars): {response_text}")
            
            # Анализ результата
            status_code = curl_data.get('status_code')
            
            if status_code == 200:
                print("\n✅ SAMO API РАБОТАЕТ!")
                print("   IP 46.250.234.89 в whitelist")
                try:
                    # Попробуем парсить JSON ответ
                    if response_text.startswith('[') or response_text.startswith('{'):
                        print("   Получен валидный JSON ответ")
                    else:
                        print("   Получен XML/текстовый ответ")
                except:
                    pass
                    
            elif status_code == 403:
                print("\n❌ SAMO API ЗАБЛОКИРОВАН")
                print("   IP 46.250.234.89 НЕ в whitelist")
                
            elif status_code == 500:
                print("\n⚠️ SAMO API - ВНУТРЕННЯЯ ОШИБКА")
                print("   Возможно IP заблокирован или проблемы с токеном")
                
            else:
                print(f"\n⚠️ НЕОЖИДАННЫЙ СТАТУС: {status_code}")
                
        else:
            print(f"❌ Ошибка curl endpoint: HTTP {curl_response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    
    # Также проверим диагностику SAMO
    try:
        print("\n🔍 Диагностика SAMO API...")
        
        samo_response = requests.get(f"{production_url}/api/diagnostics/samo", timeout=15)
        if samo_response.status_code == 200:
            samo_data = samo_response.json()
            
            dns_status = samo_data.get('tests', {}).get('dns_resolution', {}).get('status')
            api_status = samo_data.get('tests', {}).get('api_endpoint', {}).get('status_code')
            
            print(f"   DNS Resolution: {dns_status}")
            print(f"   API Status Code: {api_status}")
            
            if api_status == 200:
                print("   ✅ Диагностика подтверждает: SAMO API работает")
            elif api_status == 403:
                print("   ❌ Диагностика подтверждает: IP заблокирован")
            elif api_status == 500:
                print("   ⚠️ Диагностика показывает: Внутренняя ошибка сервера")
                
        else:
            print(f"   ❌ Ошибка диагностики: HTTP {samo_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка диагностики: {e}")

if __name__ == "__main__":
    test_production_samo()
    
    print(f"\n🎯 РЕКОМЕНДАЦИИ:")
    print("=" * 20)
    print("1. Если статус 200 - SAMO API работает, обновите страницу")
    print("2. Если статус 403 - IP все еще заблокирован")
    print("3. Если статус 500 - проверьте настройки токена")
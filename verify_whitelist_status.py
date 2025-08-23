#!/usr/bin/env python3
"""
Окончательная проверка whitelist статуса для продакшн сервера
"""

import requests
import json

def verify_production_whitelist():
    """Проверка whitelist статуса продакшн сервера"""
    
    print("🎯 ОКОНЧАТЕЛЬНАЯ ПРОВЕРКА WHITELIST")
    print("=" * 40)
    
    production_server = "46.250.234.89:5000"
    
    # 1. Проверяем IP продакшн сервера
    try:
        print("1️⃣ Получение IP продакшн сервера...")
        server_info = requests.get(f"http://{production_server}/api/diagnostics/server", timeout=15)
        
        if server_info.status_code == 200:
            data = server_info.json()
            server_ip = data.get("external_ip", "Unknown")
            print(f"   📍 IP продакшн сервера: {server_ip}")
        else:
            print(f"   ❌ Ошибка получения IP: HTTP {server_info.status_code}")
            return
            
    except Exception as e:
        print(f"   ❌ Ошибка подключения: {e}")
        return
    
    # 2. Тестируем серверный curl
    try:
        print("\n2️⃣ Тест серверного curl...")
        curl_test = requests.post(f"http://{production_server}/api/samo/server-curl-test", timeout=30)
        
        if curl_test.status_code == 200:
            curl_data = curl_test.json()
            
            http_code = curl_data.get("http_code", "000")
            response = curl_data.get("response", "")
            
            print(f"   📊 HTTP Code: {http_code}")
            print(f"   📄 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            
            if http_code == "200":
                print("\n✅ УСПЕХ! ПРОДАКШН СЕРВЕР В WHITELIST")
                print("   SAMO API полностью функционален")
                return True
                
            elif http_code == "403":
                print("\n❌ ПРОДАКШН СЕРВЕР НЕ В WHITELIST")
                print("   HTTP 403 - IP заблокирован")
                
                # Проверяем сообщение об ошибке
                if "blacklisted" in response.lower():
                    print(f"   🔍 Подтверждение: {response}")
                    
                return False
                
            elif http_code == "500":
                print("\n⚠️ НЕОПРЕДЕЛЕННЫЙ СТАТУС")
                print("   HTTP 500 - возможно заблокирован или проблема с токеном")
                return False
                
            else:
                print(f"\n⚠️ НЕОЖИДАННЫЙ HTTP КОД: {http_code}")
                return False
                
        else:
            print(f"   ❌ Ошибка curl теста: HTTP {curl_test.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Ошибка curl теста: {e}")
        return False
    
    # 3. Проверяем диагностику SAMO
    try:
        print("\n3️⃣ Диагностика SAMO API...")
        samo_diag = requests.get(f"http://{production_server}/api/diagnostics/samo", timeout=15)
        
        if samo_diag.status_code == 200:
            samo_data = samo_diag.json()
            
            api_status = samo_data.get("tests", {}).get("api_endpoint", {}).get("status_code")
            dns_status = samo_data.get("tests", {}).get("dns_resolution", {}).get("status")
            
            print(f"   📡 DNS Status: {dns_status}")
            print(f"   🌐 API Status: {api_status}")
            
            if api_status == 200:
                print("   ✅ Диагностика подтверждает: SAMO API работает")
                return True
            elif api_status == 403:
                print("   ❌ Диагностика подтверждает: IP заблокирован")
                return False
            elif api_status == 500:
                print("   ⚠️ Диагностика показывает: Проблемы с подключением")
                return False
                
        else:
            print(f"   ❌ Ошибка диагностики: HTTP {samo_diag.status_code}")
            
    except Exception as e:
        print(f"   ❌ Ошибка диагностики: {e}")

def main():
    result = verify_production_whitelist()
    
    print(f"\n🎯 ФИНАЛЬНОЕ ЗАКЛЮЧЕНИЕ:")
    print("=" * 30)
    
    if result is True:
        print("✅ ПРОДАКШН СЕРВЕР 46.250.234.89 В WHITELIST")
        print("   SAMO API работает корректно")
        print("   Статус должен показывать 'Подключен'")
        print("\n📋 Действия:")
        print("   1. Обновите страницу SAMO тестирования")
        print("   2. Статус изменится на зеленый")
        print("   3. Все функции SAMO API заработают")
        
    elif result is False:
        print("❌ ПРОДАКШН СЕРВЕР 46.250.234.89 НЕ В WHITELIST")
        print("   Требуется добавление IP в whitelist")
        print("\n📋 Действия:")
        print("   1. Обратиться в техподдержку SAMO")
        print("   2. Запросить добавление IP 46.250.234.89")
        print("   3. Указать OAuth токен для проверки")
        
    else:
        print("⚠️ СТАТУС НЕОПРЕДЕЛЕН")
        print("   Требуется дополнительная диагностика")
        print("\n📋 Действия:")
        print("   1. Проверить настройки токена")
        print("   2. Убедиться что IP действительно разблокирован")
        print("   3. Попробовать тест через некоторое время")

if __name__ == "__main__":
    main()
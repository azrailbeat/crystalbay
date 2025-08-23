#!/usr/bin/env python3
"""
Тест SAMO API whitelist статуса для сервера 46.250.234.89
"""

import requests
import json

def test_samo_whitelist():
    """Детальная проверка whitelist статуса SAMO API"""
    
    print("🔍 ТЕСТ WHITELIST СТАТУСА SAMO API")
    print("=" * 40)
    
    # Параметры для тестирования
    samo_url = "https://booking.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    # Данные для POST запроса
    data = {
        'samo_action': 'api',
        'version': '1.0', 
        'type': 'json',
        'action': 'SearchTour_CURRENCIES',
        'oauth_token': oauth_token
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Crystal Bay Travel Production/1.0'
    }
    
    print(f"📍 URL: {samo_url}")
    print(f"🔑 Token: {oauth_token[-4:]}...")
    print(f"🎯 Action: SearchTour_CURRENCIES")
    print()
    
    try:
        # Выполняем запрос с подробной информацией
        response = requests.post(
            samo_url,
            data=data,
            headers=headers,
            timeout=30,
            allow_redirects=True
        )
        
        print(f"📊 HTTP Status Code: {response.status_code}")
        print(f"🌐 Final URL: {response.url}")
        print(f"📝 Response Headers:")
        for header, value in response.headers.items():
            print(f"   {header}: {value}")
        
        print(f"\n📄 Response Body (first 500 chars):")
        response_text = response.text[:500]
        print(f"'{response_text}'")
        if len(response.text) > 500:
            print(f"... (total {len(response.text)} characters)")
        
        # Анализ статуса
        print(f"\n🔍 АНАЛИЗ РЕЗУЛЬТАТА:")
        print("=" * 25)
        
        if response.status_code == 200:
            print("✅ HTTP 200 - Сервер в whitelist!")
            try:
                data = response.json()
                print(f"✅ Получен валидный JSON с данными")
                print(f"📊 Количество валют: {len(data) if isinstance(data, list) else 'N/A'}")
            except:
                print("⚠️ Ответ не является валидным JSON")
                
        elif response.status_code == 403:
            print("❌ HTTP 403 - IP НЕ в whitelist")
            print("   Требуется добавление IP в whitelist у SAMO")
            
        elif response.status_code == 500:
            print("⚠️ HTTP 500 - Внутренняя ошибка сервера")
            print("   Возможные причины:")
            print("   - IP заблокирован/не в whitelist")
            print("   - Неверный OAuth token")
            print("   - Проблемы на стороне SAMO API")
            
        elif response.status_code == 404:
            print("❌ HTTP 404 - Endpoint не найден")
            print("   Проверьте URL API")
            
        else:
            print(f"⚠️ HTTP {response.status_code} - Неожиданный статус")
        
        return response.status_code
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Превышено время ожидания")
        print("   Возможно IP заблокирован")
        return -1
        
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR - Ошибка подключения")
        print("   Проверьте интернет-соединение")
        return -2
        
    except Exception as e:
        print(f"❌ ERROR - Неизвестная ошибка: {e}")
        return -3

def test_from_production_server():
    """Проверка с продакшн сервера 46.250.234.89"""
    
    print(f"\n🚀 ТЕСТ С ПРОДАКШН СЕРВЕРА")
    print("=" * 30)
    
    try:
        # Получаем данные диагностики с продакшн сервера
        response = requests.get(
            "http://46.250.234.89:5000/api/diagnostics/samo",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"📊 Статус с продакшн сервера:")
            print(f"   DNS Resolution: {data.get('tests', {}).get('dns_resolution', {}).get('status', 'N/A')}")
            
            api_test = data.get('tests', {}).get('api_endpoint', {})
            api_status = api_test.get('status_code', 'N/A')
            
            print(f"   API Status Code: {api_status}")
            
            if api_status == 200:
                print("✅ СЕРВЕР В WHITELIST - SAMO API работает!")
            elif api_status == 403:
                print("❌ СЕРВЕР НЕ в whitelist - 403 Forbidden")
            elif api_status == 500:
                print("⚠️ СЕРВЕР возможно НЕ в whitelist - 500 Internal Error")
            else:
                print(f"⚠️ Неопределенный статус: {api_status}")
                
        else:
            print(f"❌ Не удалось получить данные с продакшн сервера: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка подключения к продакшн серверу: {e}")

if __name__ == "__main__":
    # Тест напрямую из разработки
    status_code = test_samo_whitelist()
    
    # Тест с продакшн сервера
    test_from_production_server()
    
    print(f"\n🎯 ИТОГОВОЕ ЗАКЛЮЧЕНИЕ:")
    print("=" * 25)
    
    if status_code == 200:
        print("✅ СЕРВЕР 46.250.234.89 В WHITELIST!")
        print("   SAMO API полностью функционален")
    elif status_code == 403:
        print("❌ СЕРВЕР 46.250.234.89 НЕ В WHITELIST")
        print("   Требуется обращение в техподдержку SAMO")
    elif status_code == 500:
        print("⚠️ СТАТУС НЕОПРЕДЕЛЕН (HTTP 500)")
        print("   Скорее всего IP не в whitelist")
        print("   Рекомендация: обратиться в SAMO за разблокировкой")
    else:
        print("❌ ПРОБЛЕМЫ С ПОДКЛЮЧЕНИЕМ")
        print("   Проверьте сетевые настройки")
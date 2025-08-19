#!/usr/bin/env python3
"""
Скрипт для диагностики проблем на продакшн сервере
"""
import requests
import json
import socket
import ssl
from datetime import datetime

def test_samo_api():
    """Тест SAMO API с детальным логированием"""
    print("=" * 60)
    print("ДИАГНОСТИКА SAMO API - Crystal Bay Travel")
    print("=" * 60)
    
    # Параметры
    url = "https://booking.crystalbay.com/export/default.php"
    oauth_token = "27bd59a7ac67422189789f0188167379"
    
    # Получить IP сервера
    try:
        ip_response = requests.get("https://httpbin.org/ip", timeout=10)
        server_ip = ip_response.json().get("origin", "Unknown")
        print(f"🌐 IP сервера: {server_ip}")
    except:
        server_ip = "Unknown"
        print("❌ Не удалось определить IP сервера")
    
    # DNS проверка
    try:
        socket.gethostbyname("booking.crystalbay.com")
        print("✅ DNS разрешение: OK")
    except Exception as e:
        print(f"❌ DNS разрешение: {e}")
        return
    
    # SSL проверка
    try:
        context = ssl.create_default_context()
        with socket.create_connection(("booking.crystalbay.com", 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="booking.crystalbay.com") as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL сертификат: {dict(x[0] for x in cert['subject'])['commonName']}")
    except Exception as e:
        print(f"❌ SSL сертификат: {e}")
    
    # SAMO API тест
    params = {
        'samo_action': 'api',
        'version': '1.0',
        'type': 'json',
        'action': 'SearchTour_CURRENCIES',
        'oauth_token': oauth_token
    }
    
    headers = {
        'User-Agent': 'Crystal Bay Travel Production/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print("\n📡 Тестирование SAMO API...")
    print(f"URL: {url}")
    print(f"OAuth Token: ***{oauth_token[-4:]}")
    print(f"Action: {params['action']}")
    
    try:
        response = requests.post(url, data=params, headers=headers, timeout=15)
        
        print(f"\n📊 РЕЗУЛЬТАТ:")
        print(f"HTTP Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
        print(f"Response Length: {len(response.text)} bytes")
        
        if response.status_code == 200:
            try:
                json_data = response.json()
                print("✅ JSON парсинг: OK")
                print(f"Структура ответа: {list(json_data.keys()) if isinstance(json_data, dict) else type(json_data)}")
            except json.JSONDecodeError:
                print("❌ JSON парсинг: FAIL")
                print(f"Первые 200 символов ответа: {response.text[:200]}")
        elif response.status_code == 403:
            print("❌ 403 Forbidden - проблема с IP whitelist или OAuth токеном")
            print(f"Ответ сервера: {response.text[:300]}")
        elif response.status_code == 404:
            print("❌ 404 Not Found - проверьте URL API")
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            print(f"Ответ: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print("❌ Timeout - превышено время ожидания")
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - проблема с сетью")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 60)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 60)
    
    if server_ip != "Unknown":
        print(f"1. Добавить IP {server_ip} в whitelist SAMO API")
    print("2. Проверить активность OAuth токена")
    print("3. Связаться с поддержкой SAMO API")
    print("4. Использовать curl команду для прямого тестирования")
    
    print(f"\n📋 Curl команда:")
    print(f"curl -X POST '{url}' \\")
    print(f"  -H 'User-Agent: Crystal Bay Travel Production/1.0' \\")
    print(f"  -H 'Accept: application/json' \\")
    print(f"  -H 'Content-Type: application/x-www-form-urlencoded' \\")
    print(f"  -d 'samo_action=api&version=1.0&type=json&action=SearchTour_CURRENCIES&oauth_token={oauth_token}' \\")
    print(f"  -v --connect-timeout 15 --max-time 30")

if __name__ == "__main__":
    test_samo_api()
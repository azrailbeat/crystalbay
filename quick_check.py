#!/usr/bin/env python3
"""
Быстрая проверка синхронизации продакшн сервера
"""

import requests
import json
import sys

def check_production_sync():
    """Проверка синхронизации кода на продакшн сервере"""
    
    server = "46.250.234.89:5000"
    base_url = f"http://{server}"
    
    print("🔍 БЫСТРАЯ ПРОВЕРКА ПРОДАКШН СЕРВЕРА")
    print("=" * 40)
    print(f"📍 Сервер: {server}")
    print()
    
    results = {
        "server": server,
        "tests": {},
        "status": "unknown"
    }
    
    # 1. Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200 and "healthy" in response.text:
            print("✅ Health endpoint работает")
            results["tests"]["health"] = True
        else:
            print(f"❌ Health endpoint: HTTP {response.status_code}")
            results["tests"]["health"] = False
    except Exception as e:
        print(f"❌ Health endpoint: {str(e)}")
        results["tests"]["health"] = False
        return results
    
    # 2. Проверка API endpoints (должны возвращать JSON)
    api_endpoints = [
        "environment", "server", "network", "samo"
    ]
    
    json_endpoints = 0
    for endpoint in api_endpoints:
        try:
            response = requests.get(f"{base_url}/api/diagnostics/{endpoint}", timeout=10)
            if response.status_code == 200:
                try:
                    response.json()  # Проверяем что это валидный JSON
                    print(f"✅ API {endpoint}: JSON ответ")
                    json_endpoints += 1
                    results["tests"][f"api_{endpoint}"] = True
                except:
                    print(f"❌ API {endpoint}: HTML ответ (старая версия)")
                    results["tests"][f"api_{endpoint}"] = False
            else:
                print(f"❌ API {endpoint}: HTTP {response.status_code}")
                results["tests"][f"api_{endpoint}"] = False
        except Exception as e:
            print(f"❌ API {endpoint}: {str(e)}")
            results["tests"][f"api_{endpoint}"] = False
    
    # 3. Проверка curl функций
    try:
        payload = {"method": "SearchTour_CURRENCIES", "params": ""}
        response = requests.post(
            f"{base_url}/api/samo/execute-curl",
            json=payload,
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            if "command" in data and "status_code" in data:
                print("✅ Curl функции: JSON ответ")
                results["tests"]["curl_functions"] = True
                
                # Проверяем статус SAMO API
                if data.get("status_code") == 403:
                    print("   ⚠️  SAMO API блокирует IP (ожидаемо)")
            else:
                print("❌ Curl функции: некорректный JSON")
                results["tests"]["curl_functions"] = False
        else:
            print(f"❌ Curl функции: HTTP {response.status_code}")
            results["tests"]["curl_functions"] = False
    except Exception as e:
        print(f"❌ Curl функции: {str(e)}")
        results["tests"]["curl_functions"] = False
    
    # 4. Получение IP
    try:
        response = requests.get(f"{base_url}/api/diagnostics/server", timeout=10)
        if response.status_code == 200:
            data = response.json()
            current_ip = data.get("external_ip", "Unknown")
            print(f"📍 IP сервера: {current_ip}")
            results["current_ip"] = current_ip
    except:
        print("❌ Не удалось получить IP сервера")
    
    # Итоговая оценка
    total_tests = len(results["tests"])
    passed_tests = sum(results["tests"].values())
    
    print()
    print("🎯 РЕЗУЛЬТАТ ПРОВЕРКИ")
    print("=" * 20)
    print(f"📊 Пройдено: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 СЕРВЕР ПОЛНОСТЬЮ СИНХРОНИЗИРОВАН")
        results["status"] = "synced"
        return_code = 0
    elif passed_tests >= total_tests * 0.7:
        print("⚠️  СЕРВЕР ЧАСТИЧНО СИНХРОНИЗИРОВАН")
        print("   Большинство компонентов работает")
        results["status"] = "partial"
        return_code = 1
    else:
        print("❌ СЕРВЕР НЕ СИНХРОНИЗИРОВАН")
        print("   Требуется обновление кода")
        results["status"] = "not_synced"
        return_code = 2
    
    # Рекомендации
    if results["status"] != "synced":
        print()
        print("📋 РЕКОМЕНДАЦИИ:")
        print("1. ssh root@46.250.234.89")
        print("2. cd ~/crystalbay")
        print("3. docker-compose down")
        print("4. Обновить файлы app_api.py и templates/samo_testing.html")
        print("5. docker-compose build --no-cache")
        print("6. docker-compose up -d")
    
    # Сохраняем результаты
    with open("production_check_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Результаты сохранены в production_check_results.json")
    
    return return_code

if __name__ == "__main__":
    try:
        exit_code = check_production_sync()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Проверка прервана")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(4)
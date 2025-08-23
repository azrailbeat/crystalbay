#!/usr/bin/env python3
"""
Быстрая проверка здоровья системы Crystal Bay Travel
"""

import requests
import json
import sys
from datetime import datetime

def health_check():
    """Проверка основных компонентов системы"""
    
    base_url = "http://localhost:5000"
    results = {
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "checks": {}
    }
    
    print("🏥 ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ Crystal Bay Travel")
    print("=" * 50)
    
    # 1. Базовая проверка
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            results["checks"]["health_endpoint"] = "✅ Работает"
            print("✅ Health endpoint: Работает")
        else:
            results["checks"]["health_endpoint"] = f"❌ HTTP {response.status_code}"
            print(f"❌ Health endpoint: HTTP {response.status_code}")
    except Exception as e:
        results["checks"]["health_endpoint"] = f"❌ {str(e)}"
        print(f"❌ Health endpoint: {str(e)}")
        return results
    
    # 2. Главная страница
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200 and "Crystal Bay" in response.text:
            results["checks"]["main_page"] = "✅ Работает"
            print("✅ Главная страница: Работает")
        else:
            results["checks"]["main_page"] = "❌ Ошибка загрузки"
            print("❌ Главная страница: Ошибка загрузки")
    except Exception as e:
        results["checks"]["main_page"] = f"❌ {str(e)}"
        print(f"❌ Главная страница: {str(e)}")
    
    # 3. API диагностики
    endpoints = [
        "/api/diagnostics/environment",
        "/api/diagnostics/server", 
        "/api/diagnostics/network",
        "/api/diagnostics/samo"
    ]
    
    api_working = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                api_working += 1
                results["checks"][f"api{endpoint.split('/')[-1]}"] = "✅ Работает"
                print(f"✅ API {endpoint.split('/')[-1]}: Работает")
            else:
                results["checks"][f"api{endpoint.split('/')[-1]}"] = f"❌ HTTP {response.status_code}"
                print(f"❌ API {endpoint.split('/')[-1]}: HTTP {response.status_code}")
        except Exception as e:
            results["checks"][f"api{endpoint.split('/')[-1]}"] = f"❌ {str(e)}"
            print(f"❌ API {endpoint.split('/')[-1]}: {str(e)}")
    
    # 4. SAMO API статус
    try:
        response = requests.get(f"{base_url}/api/diagnostics/samo", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if "tests" in data and "api_endpoint" in data["tests"]:
                api_test = data["tests"]["api_endpoint"]
                if api_test["status_code"] == 403:
                    results["checks"]["samo_api"] = "⚠️ IP заблокирован"
                    print("⚠️ SAMO API: IP заблокирован у поставщика")
                elif api_test["status_code"] == 200:
                    results["checks"]["samo_api"] = "✅ Работает"
                    print("✅ SAMO API: Работает")
                else:
                    results["checks"]["samo_api"] = f"❌ HTTP {api_test['status_code']}"
                    print(f"❌ SAMO API: HTTP {api_test['status_code']}")
    except Exception as e:
        results["checks"]["samo_api"] = f"❌ {str(e)}"
        print(f"❌ SAMO API: {str(e)}")
    
    # 5. Curl функции
    try:
        payload = {"method": "SearchTour_CURRENCIES", "params": ""}
        response = requests.post(f"{base_url}/api/samo/execute-curl", json=payload, timeout=15)
        if response.status_code == 200:
            results["checks"]["curl_functions"] = "✅ Работают"
            print("✅ Curl функции: Работают")
        else:
            results["checks"]["curl_functions"] = f"❌ HTTP {response.status_code}"
            print(f"❌ Curl функции: HTTP {response.status_code}")
    except Exception as e:
        results["checks"]["curl_functions"] = f"❌ {str(e)}"
        print(f"❌ Curl функции: {str(e)}")
    
    # Итоговый статус
    working_count = len([v for v in results["checks"].values() if v.startswith("✅")])
    warning_count = len([v for v in results["checks"].values() if v.startswith("⚠️")])
    total_count = len(results["checks"])
    
    print("\n" + "=" * 50)
    print("📊 ИТОГОВЫЙ СТАТУС:")
    print(f"✅ Работает: {working_count}/{total_count}")
    print(f"⚠️ Предупреждения: {warning_count}")
    
    if working_count >= total_count * 0.8:  # 80% работает
        results["status"] = "healthy"
        print("🎉 СИСТЕМА РАБОТАЕТ НОРМАЛЬНО")
    elif working_count >= total_count * 0.6:  # 60% работает
        results["status"] = "degraded"
        print("⚠️ СИСТЕМА РАБОТАЕТ С ОГРАНИЧЕНИЯМИ")
    else:
        results["status"] = "unhealthy"
        print("🚨 СИСТЕМА ТРЕБУЕТ ВНИМАНИЯ")
    
    # Сохраняем результаты
    with open("health_check_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Результаты сохранены в health_check_results.json")
    return results

if __name__ == "__main__":
    try:
        results = health_check()
        if results["status"] == "healthy":
            sys.exit(0)
        elif results["status"] == "degraded":
            sys.exit(1)
        else:
            sys.exit(2)
    except KeyboardInterrupt:
        print("\n❌ Проверка прервана")
        sys.exit(3)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(4)
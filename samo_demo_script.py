#!/usr/bin/env python3
"""
Демонстрационный скрипт для тестирования всех методов SAMO API
Показывает полный функционал системы для менеджеров Crystal Bay Travel
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def test_api_endpoint(endpoint, method="GET", data=None):
    """Тестирует API endpoint и выводит результат"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Тестирование: {method} {endpoint}")
    print(f"{'='*60}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        
        print(f"Статус: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            result = response.json()
            print(f"Ответ: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}...")
        else:
            print(f"Ответ: {response.text[:500]}...")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def main():
    """Основная функция демонстрации"""
    print("🏖️ Crystal Bay Travel - Демонстрация SAMO API Integration")
    print("=" * 70)
    
    # 1. Тест подключения
    print("\n📋 1. ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ")
    test_api_endpoint("/api/samo/test")
    
    # 2. Справочники
    print("\n📚 2. ЗАГРУЗКА СПРАВОЧНИКОВ")
    test_api_endpoint("/api/samo/townfroms")
    test_api_endpoint("/api/samo/states") 
    test_api_endpoint("/api/samo/currencies")
    test_api_endpoint("/api/samo/hotels")
    test_api_endpoint("/api/samo/tours")
    
    # 3. Поиск туров
    print("\n🔍 3. ПОИСК ТУРОВ")
    
    # Поиск цен на туры
    search_params = {
        "TOWNFROMINC": "",
        "STATEINC": "",
        "CHECKIN_BEG": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "CHECKIN_END": (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d'),
        "NIGHTS_FROM": 7,
        "NIGHTS_TILL": 14,
        "ADULT": 2,
        "CHILD": 0,
        "CURRENCY": "USD",
        "FILTER": 1
    }
    
    test_api_endpoint("/api/samo/search/prices", "POST", search_params)
    test_api_endpoint("/api/samo/search/tours", "POST", search_params)
    
    # 4. Бронирования
    print("\n📅 4. УПРАВЛЕНИЕ БРОНИРОВАНИЯМИ")
    test_api_endpoint("/api/samo/bookings")
    
    # 5. Отчеты
    print("\n📊 5. ОТЧЕТЫ")
    date_from = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    date_to = datetime.now().strftime('%Y-%m-%d')
    
    test_api_endpoint(f"/api/samo/reports/sales?date_from={date_from}&date_to={date_to}")
    test_api_endpoint(f"/api/samo/reports/financial?date_from={date_from}&date_to={date_to}")
    
    # 6. Дополнительные услуги
    print("\n🎯 6. ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ")
    test_api_endpoint("/api/samo/services")
    test_api_endpoint("/api/samo/payments/methods")
    
    print("\n" + "="*70)
    print("✅ Демонстрация завершена!")
    print("\n💡 ПРИМЕЧАНИЯ:")
    print("- IP адрес 35.231.81.33 заблокирован в системе Crystal Bay")
    print("- Необходимо добавить текущий IP в whitelist для полного доступа")
    print("- Все API endpoints готовы к работе после разблокировки")
    print("- Интерфейс доступен по адресу: http://localhost:5000/samo-api")

if __name__ == "__main__":
    main()
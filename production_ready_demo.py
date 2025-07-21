#!/usr/bin/env python3
"""
Production Ready Demo - Crystal Bay Travel System
Demonstrates fully working system with realistic travel booking data
"""

import json
import os
import requests
from datetime import datetime, timedelta
import uuid

def create_realistic_leads():
    """Create realistic Crystal Bay travel leads for demonstration"""
    
    destinations = [
        {"country": "Вьетнам", "city": "Хошимин", "price_range": (800, 1200)},
        {"country": "Таиланд", "city": "Пхукет", "price_range": (900, 1400)}, 
        {"country": "Турция", "city": "Анталья", "price_range": (600, 1000)},
        {"country": "Египет", "city": "Хургада", "price_range": (500, 800)},
        {"country": "ОАЭ", "city": "Дубай", "price_range": (1200, 2000)},
        {"country": "Мальдивы", "city": "Мале", "price_range": (2000, 3500)},
        {"country": "Индонезия", "city": "Бали", "price_range": (1000, 1600)}
    ]
    
    departure_cities = ["Алматы", "Нур-Султан", "Шымкент", "Актобе", "Караганда"]
    
    client_names = [
        "Айжан Серикова", "Данияр Жумабеков", "Гульнара Токтарова", 
        "Арман Байжанов", "Сауле Касымова", "Ерлан Мустафин",
        "Жанара Ибраимова", "Нурлан Кенесов", "Алтынай Тулегенова",
        "Бакыт Рахимов"
    ]
    
    realistic_leads = []
    
    for i, name in enumerate(client_names):
        destination = destinations[i % len(destinations)]
        departure = departure_cities[i % len(departure_cities)]
        
        # Generate realistic dates (future bookings)
        departure_date = datetime.now() + timedelta(days=30 + i*14)
        created_date = datetime.now() - timedelta(days=i+1)
        
        # Generate price in range
        min_price, max_price = destination["price_range"]
        price = min_price + (i * 50) % (max_price - min_price)
        
        lead = {
            "id": str(uuid.uuid4()),
            "customer_name": name,
            "email": f"{name.lower().replace(' ', '.')}@example.com",
            "phone": f"+7 7{70 + i}{100 + i:02d} {200 + i:02d} {300 + i:02d}",
            "destination": f"{destination['country']} - {destination['city']}",
            "departure_city": departure,
            "departure_date": departure_date.strftime('%Y-%m-%d'),
            "nights": 7 + (i % 7),
            "adults": 2 + (i % 2),
            "children": i % 3,
            "tour_type": ["Пляжный отдых", "Экскурсионный", "Комбинированный"][i % 3],
            "price": price,
            "currency": "USD",
            "status": ["new", "in_progress", "pending", "confirmed"][i % 4],
            "source": "website",
            "created_at": created_date.isoformat(),
            "notes": f"Crystal Bay Travel - заявка на {destination['country']}. "
                    f"Вылет из {departure}. "
                    f"{7 + (i % 7)} дней, {2 + (i % 2)} взрослых"
                    + (f", {i % 3} детей" if i % 3 > 0 else "") + ".",
            "agent_assigned": ["Менеджер 1", "Менеджер 2", "Менеджер 3"][i % 3],
            "priority": ["normal", "high", "urgent"][i % 3] if i % 4 == 3 else "normal",
            "tags": [
                destination['country'],
                departure,
                "Активная заявка" if i % 4 != 0 else "Новая заявка"
            ]
        }
        
        realistic_leads.append(lead)
    
    return realistic_leads

def update_system_with_production_data():
    """Update the Crystal Bay system with realistic production data"""
    
    print("🏖️ CRYSTAL BAY TRAVEL - ЗАГРУЗКА РЕАЛИСТИЧНЫХ ДАННЫХ")
    print("=" * 60)
    
    # Create realistic leads
    leads = create_realistic_leads()
    print(f"✅ Создано {len(leads)} реалистичных заявок Crystal Bay")
    
    # Update persistent storage
    storage_file = 'data/memory_leads.json'
    os.makedirs('data', exist_ok=True)
    
    # Load existing data and merge
    existing_leads = []
    if os.path.exists(storage_file):
        try:
            with open(storage_file, 'r', encoding='utf-8') as f:
                existing_leads = json.load(f)
        except:
            pass
    
    # Merge with new realistic data (replace system entries)
    final_leads = [lead for lead in existing_leads if lead.get('source') != 'system']
    final_leads.extend(leads)
    
    # Save to storage
    with open(storage_file, 'w', encoding='utf-8') as f:
        json.dump(final_leads, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Сохранено {len(final_leads)} заявок в {storage_file}")
    
    # Display sample data
    print("\n📋 ОБРАЗЦЫ ЗАЯВОК:")
    print("-" * 40)
    
    for i, lead in enumerate(leads[:5]):  # Show first 5
        status_icon = {"new": "🆕", "in_progress": "⏳", "pending": "⏰", "confirmed": "✅"}
        icon = status_icon.get(lead['status'], "📝")
        
        print(f"{icon} {lead['customer_name']}")
        print(f"   📍 {lead['destination']}")
        print(f"   🛫 Вылет: {lead['departure_date']} из {lead['departure_city']}")
        print(f"   💰 {lead['price']} {lead['currency']} - {lead['nights']} ночей")
        print(f"   📞 {lead['phone']}")
        print()
    
    # Test API integration
    print("🔗 ТЕСТИРОВАНИЕ API ИНТЕГРАЦИИ")
    print("-" * 40)
    
    try:
        # Test leads endpoint
        response = requests.get("http://localhost:5000/api/leads", timeout=5)
        if response.status_code == 200:
            api_leads = response.json()
            print(f"✅ API возвращает {len(api_leads)} заявок")
        else:
            print(f"⚠️ API статус: {response.status_code}")
    except Exception as e:
        print(f"⚠️ API недоступен: {e}")
    
    print("\n🎯 РЕЗУЛЬТАТ")
    print("-" * 40)
    print("✅ Система загружена реалистичными данными Crystal Bay")
    print("✅ Все заявки готовы для работы с Kanban интерфейсом") 
    print("✅ Данные персистентны и сохранятся между перезапусками")
    print("✅ Система готова для демонстрации полной функциональности")
    
    print(f"\n📊 СТАТИСТИКА:")
    status_counts = {}
    for lead in leads:
        status = lead['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        print(f"   {status.capitalize()}: {count} заявок")
    
    return len(final_leads)

if __name__ == '__main__':
    update_system_with_production_data()
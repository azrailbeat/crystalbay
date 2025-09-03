#!/usr/bin/env python3
"""
Простой загрузчик справочных данных SAMO API
Получает все обозначения и коды для предустановки в системе
"""

import json
import time
from samo_integration import SamoAPIIntegration

def load_samo_references():
    """Загрузка всех справочных данных SAMO"""
    print("🚀 Загружаем справочные данные SAMO API...")
    
    samo_api = SamoAPIIntegration()
    
    # Основные справочники
    commands = {
        'currencies': 'SearchTour_CURRENCIES',
        'states': 'SearchTour_STATES',
        'cities': 'SearchTour_TOWNFROMS', 
        'hotels': 'SearchTour_HOTELS',
        'stars': 'SearchTour_STARS',
        'meals': 'SearchTour_MEALS'
    }
    
    results = {}
    
    for name, command in commands.items():
        print(f"📥 Загружаем {name} ({command})...")
        
        try:
            result = samo_api._make_request(command, {})
            
            if result.get('success'):
                results[name] = result
                print(f"✅ {name} - успешно")
            else:
                print(f"⚠️ {name} - ошибка: {result.get('error', 'неизвестная ошибка')}")
                results[name] = result
                
        except Exception as e:
            print(f"❌ {name} - исключение: {e}")
            results[name] = {'success': False, 'error': str(e)}
        
        time.sleep(0.5)  # Пауза между запросами
    
    # Сохраняем результаты
    with open('samo_reference_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Данные сохранены в samo_reference_data.json")
    
    # Выводим краткую статистику
    success_count = sum(1 for r in results.values() if r.get('success'))
    total_count = len(results)
    
    print(f"📊 Статистика: {success_count}/{total_count} успешно загружено")
    
    return results

if __name__ == "__main__":
    load_samo_references()
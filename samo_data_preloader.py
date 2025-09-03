#!/usr/bin/env python3
"""
SAMO API Data Preloader для Crystal Bay Travel
Загружает все справочные данные с production SAMO API
"""

import json
import logging
import time
from typing import Dict, List, Any
from samo_integration import SamoAPIIntegration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SamoDataPreloader:
    """Загрузчик всех справочных данных SAMO API"""
    
    def __init__(self):
        self.samo_api = SamoAPIIntegration()
        self.reference_data = {}
        
        # Все справочные команды SAMO API
        self.reference_commands = {
            # Основные справочники для поиска туров
            'currencies': 'SearchTour_CURRENCIES',
            'states': 'SearchTour_STATES', 
            'departure_cities': 'SearchTour_TOWNFROMS',
            'destination_cities': 'SearchTour_TOWNS',
            'hotels': 'SearchTour_HOTELS',
            'star_ratings': 'SearchTour_STARS',
            'meal_types': 'SearchTour_MEALS',
            'tours': 'SearchTour_TOURS',
            'programs': 'SearchTour_PROGRAMS',
            'program_groups': 'SearchTour_PROGRAM_GROUPS',
            'tour_types': 'SearchTour_TOUR_TYPES',
            'tour_groups': 'SearchTour_TOUR_GROUPS',
            'product_types': 'SearchTour_PRODUCT_TYPES',
            'hotel_types': 'SearchTour_HOTEL_TYPES',
            'nights': 'SearchTour_NIGHTS',
            'adult_options': 'SearchTour_ADULT',
            'child_options': 'SearchTour_CHILD',
            
            # Дополнительные справочники
            'insurance_types': 'Insures_INSURETYPES',
            'insurance_states': 'Insures_STATES',
            'payment_variants': 'PayVariant_List',
            'currency_rates': 'Currency_RATES',
            'best_offers': 'TheBest_ALL',
            
            # Справочники для бронирования
            'booking_states': 'Booking_GetStates',
            'people_documents': 'Booking_GetPeopleDocuments'
        }
    
    def load_all_reference_data(self) -> Dict[str, Any]:
        """Загрузка всех справочных данных"""
        logger.info("🚀 Начинаем загрузку всех справочных данных SAMO API...")
        
        total_commands = len(self.reference_commands)
        completed = 0
        
        for data_type, command in self.reference_commands.items():
            try:
                logger.info(f"📥 Загружаем {data_type} ({command})...")
                
                result = self.samo_api._make_request(command, {})
                
                if result.get('success'):
                    self.reference_data[data_type] = {
                        'command': command,
                        'data': result.get('data', {}),
                        'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'success'
                    }
                    logger.info(f"✅ {data_type} загружен успешно")
                else:
                    self.reference_data[data_type] = {
                        'command': command,
                        'error': result.get('error', 'Unknown error'),
                        'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'status': 'failed'
                    }
                    logger.warning(f"⚠️ {data_type} не загружен: {result.get('error')}")
                
                completed += 1
                logger.info(f"📊 Прогресс: {completed}/{total_commands} ({completed/total_commands*100:.1f}%)")
                
                # Небольшая пауза между запросами
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки {data_type}: {e}")
                self.reference_data[data_type] = {
                    'command': command,
                    'error': str(e),
                    'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': 'error'
                }
        
        return self.reference_data
    
    def get_kazakhstan_specific_data(self) -> Dict[str, Any]:
        """Получение данных специфичных для Казахстана"""
        logger.info("🇰🇿 Загружаем данные для казахстанского рынка...")
        
        kazakhstan_data = {}
        
        # Города отправления Казахстана
        if 'departure_cities' in self.reference_data and self.reference_data['departure_cities']['status'] == 'success':
            cities_data = self.reference_data['departure_cities']['data']
            if 'SearchTour_TOWNFROMS' in cities_data:
                all_cities = cities_data['SearchTour_TOWNFROMS']
                
                # Фильтруем казахстанские города
                kz_cities = []
                for city in all_cities:
                    if 'KAZAKHSTAN' in city.get('stateFromNameAlt', '').upper() or \
                       'КАЗАХСТАН' in city.get('stateFromName', ''):
                        kz_cities.append(city)
                
                kazakhstan_data['departure_cities'] = kz_cities
                logger.info(f"✅ Найдено {len(kz_cities)} казахстанских городов отправления")
        
        # Валюты с приоритетом KZT
        if 'currencies' in self.reference_data and self.reference_data['currencies']['status'] == 'success':
            currencies_data = self.reference_data['currencies']['data']
            if 'SearchTour_CURRENCIES' in currencies_data:
                all_currencies = currencies_data['SearchTour_CURRENCIES']
                
                # Приоритет KZT, потом остальные
                kzt_currency = None
                other_currencies = []
                
                for currency in all_currencies:
                    if currency.get('name') == 'KZT':
                        kzt_currency = currency
                    else:
                        other_currencies.append(currency)
                
                ordered_currencies = []
                if kzt_currency:
                    ordered_currencies.append(kzt_currency)
                ordered_currencies.extend(other_currencies)
                
                kazakhstan_data['currencies'] = ordered_currencies
                logger.info(f"✅ Настроен приоритет валют (KZT первая)")
        
        return kazakhstan_data
    
    def save_reference_data(self, filename: str = 'samo_reference_data.json'):
        """Сохранение справочных данных в файл"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.reference_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Справочные данные сохранены в {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения данных: {e}")
            return False
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Сводка загруженных данных"""
        summary = {
            'total_commands': len(self.reference_commands),
            'successful_loads': 0,
            'failed_loads': 0,
            'error_loads': 0,
            'details': {}
        }
        
        for data_type, data_info in self.reference_data.items():
            status = data_info.get('status', 'unknown')
            
            if status == 'success':
                summary['successful_loads'] += 1
                # Подсчитываем записи в данных
                data_content = data_info.get('data', {})
                record_count = 0
                for key, value in data_content.items():
                    if isinstance(value, list):
                        record_count += len(value)
                
                summary['details'][data_type] = {
                    'status': 'success',
                    'records': record_count,
                    'command': data_info.get('command')
                }
            
            elif status == 'failed':
                summary['failed_loads'] += 1
                summary['details'][data_type] = {
                    'status': 'failed',
                    'error': data_info.get('error'),
                    'command': data_info.get('command')
                }
            
            else:
                summary['error_loads'] += 1
                summary['details'][data_type] = {
                    'status': 'error',
                    'error': data_info.get('error'),
                    'command': data_info.get('command')
                }
        
        return summary

def main():
    """Основная функция загрузки данных"""
    print("🎯 SAMO API Data Preloader для Crystal Bay Travel")
    print("=" * 60)
    
    preloader = SamoDataPreloader()
    
    # Загружаем все справочные данные
    reference_data = preloader.load_all_reference_data()
    
    # Получаем казахстанские данные
    kz_data = preloader.get_kazakhstan_specific_data()
    
    # Сохраняем данные
    preloader.save_reference_data()
    
    # Выводим сводку
    summary = preloader.get_data_summary()
    
    print("\n📊 СВОДКА ЗАГРУЗКИ ДАННЫХ:")
    print(f"✅ Успешно загружено: {summary['successful_loads']}")
    print(f"⚠️ Не удалось загрузить: {summary['failed_loads']}")
    print(f"❌ Ошибки: {summary['error_loads']}")
    print(f"📝 Всего команд: {summary['total_commands']}")
    
    print("\n🎯 ДЕТАЛИ ЗАГРУЖЕННЫХ ДАННЫХ:")
    for data_type, details in summary['details'].items():
        status_icon = "✅" if details['status'] == 'success' else "⚠️" if details['status'] == 'failed' else "❌"
        if details['status'] == 'success':
            print(f"{status_icon} {data_type}: {details['records']} записей ({details['command']})")
        else:
            print(f"{status_icon} {data_type}: {details['error']}")
    
    if kz_data:
        print(f"\n🇰🇿 ДАННЫЕ ДЛЯ КАЗАХСТАНА:")
        if 'departure_cities' in kz_data:
            print(f"🏙️ Города отправления: {len(kz_data['departure_cities'])}")
        if 'currencies' in kz_data:
            print(f"💰 Валюты (KZT приоритет): {len(kz_data['currencies'])}")
    
    print(f"\n💾 Данные сохранены в: samo_reference_data.json")
    print("🚀 Готово для интеграции в систему!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
SAMO API Data Preloader
Предварительная загрузка всех справочных данных из SAMO API при запуске приложения
"""

import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SamoDataPreloader:
    """Предзагрузчик справочных данных из SAMO API"""
    
    def __init__(self, samo_api):
        self.samo_api = samo_api
        self.preloaded_data = {}
        self.last_preload_time = None
        self.preload_duration = None
        
    def preload_all_reference_data(self) -> Dict[str, Any]:
        """
        Выполняет SearchTour_ALL и загружает все справочные данные
        для казахстанского рынка (Алматы ID: 1344 → Вьетнам ID: 15)
        """
        start_time = time.time()
        logger.info("🚀 Начинаю предварительную загрузку всех данных SAMO API...")
        
        # Параметры для казахстанского рынка
        kazakhstan_params = {
            'TOWNFROMINC': '1344',  # Алматы
            'STATEINC': '15'        # Вьетнам
        }
        
        try:
            # 1. Основной запрос SearchTour_ALL для получения всех данных
            logger.info("📋 Загружаю SearchTour_ALL для всех отелей и туров...")
            all_tours_result = self.samo_api._make_request('SearchTour_ALL', kazakhstan_params)
            
            # 2. Параллельная загрузка всех справочников
            reference_requests = {
                'currencies': ('SearchTour_CURRENCIES', kazakhstan_params),
                'states': ('SearchTour_STATES', kazakhstan_params),
                'towns_from': ('SearchTour_TOWNFROMS', kazakhstan_params),
                'stars': ('SearchTour_STARS', kazakhstan_params),
                'meals': ('SearchTour_MEALS', kazakhstan_params),
                'hotels': ('SearchTour_HOTELS', {**kazakhstan_params, 'STATEINC': '15'}),
                'programs': ('SearchTour_PROGRAMS', kazakhstan_params),
                'nights': ('NIGHTS', kazakhstan_params)
            }
            
            reference_data = {}
            success_count = 0
            
            for key, (command, params) in reference_requests.items():
                logger.info(f"📊 Загружаю {command}...")
                result = self.samo_api._make_request(command, params)
                
                if result.get('success'):
                    reference_data[key] = result.get('data', {})
                    success_count += 1
                    logger.info(f"✅ {command} загружен успешно")
                else:
                    logger.warning(f"⚠️ {command} не удалось загрузить: {result.get('error')}")
                    reference_data[key] = {}
            
            # 3. Обработка результатов SearchTour_ALL
            tours_data = {}
            hotels_list = []
            
            if all_tours_result.get('success'):
                tours_data = all_tours_result.get('data', {})
                
                # Извлекаем список отелей из данных туров
                if 'SearchTour_ALL' in tours_data and isinstance(tours_data['SearchTour_ALL'], list):
                    for tour in tours_data['SearchTour_ALL']:
                        if isinstance(tour, dict) and 'hotel_name' in tour:
                            hotel_info = {
                                'id': tour.get('hotel_id', ''),
                                'name': tour.get('hotel_name', ''),
                                'stars': tour.get('stars', 0),
                                'city': tour.get('city', ''),
                                'country': tour.get('country', 'Вьетнам')
                            }
                            if hotel_info not in hotels_list:
                                hotels_list.append(hotel_info)
                
                logger.info(f"🏨 Найдено {len(hotels_list)} уникальных отелей")
                success_count += 1
            else:
                logger.warning(f"⚠️ SearchTour_ALL не удалось загрузить: {all_tours_result.get('error')}")
            
            # 4. Формирование итогового результата
            self.preloaded_data = {
                'reference_data': reference_data,
                'tours_data': tours_data,
                'hotels_list': hotels_list,
                'kazakhstan_params': kazakhstan_params,
                'success_count': success_count,
                'total_requests': len(reference_requests) + 1,
                'load_time': time.time() - start_time,
                'loaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.last_preload_time = time.time()
            self.preload_duration = self.preloaded_data['load_time']
            
            logger.info(f"🎉 Предварительная загрузка завершена!")
            logger.info(f"📈 Успешно: {success_count}/{len(reference_requests) + 1} запросов")
            logger.info(f"⏱️ Время загрузки: {self.preload_duration:.2f} секунд")
            logger.info(f"🏨 Загружено отелей: {len(hotels_list)}")
            
            return self.preloaded_data
            
        except Exception as e:
            logger.error(f"❌ Ошибка при предварительной загрузке: {e}")
            return {
                'reference_data': {},
                'tours_data': {},
                'hotels_list': [],
                'error': str(e),
                'load_time': time.time() - start_time,
                'success_count': 0
            }
    
    def get_preloaded_data(self, data_type: str) -> Dict[str, Any]:
        """Получить предзагруженные данные по типу"""
        if not self.preloaded_data:
            logger.warning("Данные не были предварительно загружены")
            return {}
        
        if data_type == 'all':
            return self.preloaded_data
        elif data_type in ['reference_data', 'tours_data', 'hotels_list']:
            return self.preloaded_data.get(data_type, {})
        else:
            return self.preloaded_data.get('reference_data', {}).get(data_type, {})
    
    def get_hotels_for_destination(self, destination_id: str = '15') -> list:
        """Получить список отелей для конкретного направления"""
        hotels = self.preloaded_data.get('hotels_list', [])
        if destination_id == '15':  # Вьетнам
            return hotels
        return []
    
    def get_currencies_list(self) -> list:
        """Получить список валют"""
        currencies_data = self.preloaded_data.get('reference_data', {}).get('currencies', {})
        if 'SearchTour_CURRENCIES' in currencies_data:
            return currencies_data['SearchTour_CURRENCIES']
        
        # Значения по умолчанию для казахстанского рынка
        return [
            {'id': 'KZT', 'name': '₸ Казахстанский тенге'},
            {'id': 'USD', 'name': '💵 Доллар США'},
            {'id': 'RUB', 'name': '₽ Российский рубль'}
        ]
    
    def get_departure_cities_list(self) -> list:
        """Получить список городов отправления"""
        towns_data = self.preloaded_data.get('reference_data', {}).get('towns_from', {})
        if 'SearchTour_TOWNFROMS' in towns_data:
            return towns_data['SearchTour_TOWNFROMS']
        
        # Значения по умолчанию для Казахстана (ID из production SAMO API)
        return [
            {'id': 1344, 'name': 'Алматы'},
            {'id': 1937, 'name': 'Астана'}
        ]
    
    def get_destinations_list(self) -> list:
        """Получить список направлений"""
        states_data = self.preloaded_data.get('reference_data', {}).get('states', {})
        if 'SearchTour_STATES' in states_data:
            return states_data['SearchTour_STATES']
        
        # Значения по умолчанию для Вьетнама
        return [
            {'id': '15', 'name': '🇻🇳 Вьетнам'}
        ]
    
    def is_data_fresh(self, max_age_minutes: int = 30) -> bool:
        """Проверить, свежие ли предзагруженные данные"""
        if not self.last_preload_time:
            return False
        
        age_minutes = (time.time() - self.last_preload_time) / 60
        return age_minutes <= max_age_minutes
    
    def get_preload_status(self) -> Dict[str, Any]:
        """Получить статус предварительной загрузки"""
        return {
            'is_loaded': bool(self.preloaded_data),
            'load_time': self.preload_duration,
            'loaded_at': self.preloaded_data.get('loaded_at'),
            'success_count': self.preloaded_data.get('success_count', 0),
            'total_requests': self.preloaded_data.get('total_requests', 0),
            'hotels_count': len(self.preloaded_data.get('hotels_list', [])),
            'is_fresh': self.is_data_fresh(),
            'age_minutes': (time.time() - self.last_preload_time) / 60 if self.last_preload_time else None
        }

# Глобальный экземпляр предзагрузчика
_preloader_instance = None

def initialize_preloader(samo_api):
    """Инициализация глобального экземпляра предзагрузчика"""
    global _preloader_instance
    _preloader_instance = SamoDataPreloader(samo_api)
    return _preloader_instance

def get_preloader():
    """Получить глобальный экземпляр предзагрузчика"""
    return _preloader_instance

def preload_samo_data(samo_api):
    """Удобная функция для предварительной загрузки данных"""
    preloader = initialize_preloader(samo_api)
    return preloader.preload_all_reference_data()
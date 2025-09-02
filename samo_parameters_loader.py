#!/usr/bin/env python3
"""
Загрузка реальных параметров из SAMO API для форм поиска
"""

import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class SamoParametersLoader:
    """Загрузчик параметров из SAMO API"""
    
    def __init__(self):
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            self.samo_api = CrystalBaySamoAPI()
            logger.info("SAMO Parameters Loader initialized")
        except ImportError:
            logger.error("Failed to import SAMO API")
            self.samo_api = None
    
    def get_all_search_parameters(self) -> Dict[str, Any]:
        """Получить все параметры поиска из SAMO API"""
        if not self.samo_api:
            return self._get_fallback_parameters()
        
        parameters = {
            'currencies': [],
            'destinations': [],
            'departure_cities': [],
            'hotels': [],
            'stars': [],
            'meals': [],
            'error': None,
            'loaded_at': datetime.now().isoformat()
        }
        
        try:
            # 1. Валюты
            logger.info("Loading currencies from SAMO...")
            currencies_result = self.samo_api._make_request('SearchTour_CURRENCIES', {
                'action': 'SearchTour_CURRENCIES'
            })
            
            if currencies_result.get('success'):
                data = currencies_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_CURRENCIES' in data:
                    currencies_list = data['SearchTour_CURRENCIES']
                    if isinstance(currencies_list, list):
                        parameters['currencies'] = [
                            {
                                'id': curr.get('id', curr.get('code', '')),
                                'code': curr.get('code', ''),
                                'name': curr.get('name', curr.get('code', '')),
                                'rate': curr.get('rate', 1)
                            }
                            for curr in currencies_list
                        ]
                        logger.info(f"Loaded {len(parameters['currencies'])} currencies")
            
            # 2. Страны/направления
            logger.info("Loading destinations from SAMO...")
            states_result = self.samo_api._make_request('SearchTour_STATES', {
                'action': 'SearchTour_STATES'
            })
            
            if states_result.get('success'):
                data = states_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_STATES' in data:
                    states_list = data['SearchTour_STATES']
                    if isinstance(states_list, list):
                        parameters['destinations'] = [
                            {
                                'id': state.get('id', ''),
                                'name': state.get('name', ''),
                                'code': state.get('code', ''),
                                'alt_name': state.get('alt_name', '')
                            }
                            for state in states_list
                        ]
                        logger.info(f"Loaded {len(parameters['destinations'])} destinations")
            
            # 3. Города отправления
            logger.info("Loading departure cities from SAMO...")
            towns_result = self.samo_api._make_request('SearchTour_TOWNFROMS', {
                'action': 'SearchTour_TOWNFROMS'
            })
            
            if towns_result.get('success'):
                data = towns_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_TOWNFROMS' in data:
                    towns_list = data['SearchTour_TOWNFROMS']
                    if isinstance(towns_list, list):
                        parameters['departure_cities'] = [
                            {
                                'id': town.get('id', ''),
                                'name': town.get('name', ''),
                                'code': town.get('code', ''),
                                'country': town.get('country', '')
                            }
                            for town in towns_list
                        ]
                        logger.info(f"Loaded {len(parameters['departure_cities'])} departure cities")
            
            # 4. Звездности отелей
            logger.info("Loading hotel stars from SAMO...")
            stars_result = self.samo_api._make_request('SearchTour_STARS', {
                'action': 'SearchTour_STARS'
            })
            
            if stars_result.get('success'):
                data = stars_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_STARS' in data:
                    stars_list = data['SearchTour_STARS']
                    if isinstance(stars_list, list):
                        parameters['stars'] = [
                            {
                                'id': star.get('id', ''),
                                'name': star.get('name', ''),
                                'value': star.get('value', star.get('stars', ''))
                            }
                            for star in stars_list
                        ]
                        logger.info(f"Loaded {len(parameters['stars'])} star categories")
            
            # 5. Типы питания
            logger.info("Loading meal types from SAMO...")
            meals_result = self.samo_api._make_request('SearchTour_MEALS', {
                'action': 'SearchTour_MEALS'
            })
            
            if meals_result.get('success'):
                data = meals_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_MEALS' in data:
                    meals_list = data['SearchTour_MEALS']
                    if isinstance(meals_list, list):
                        parameters['meals'] = [
                            {
                                'id': meal.get('id', ''),
                                'name': meal.get('name', ''),
                                'code': meal.get('code', ''),
                                'description': meal.get('description', '')
                            }
                            for meal in meals_list
                        ]
                        logger.info(f"Loaded {len(parameters['meals'])} meal types")
            
            # 6. Отели (ограниченный список для производительности)
            logger.info("Loading hotels from SAMO...")
            hotels_result = self.samo_api._make_request('SearchTour_HOTELS', {
                'action': 'SearchTour_HOTELS',
                'limit': '100'  # Ограничиваем количество для производительности
            })
            
            if hotels_result.get('success'):
                data = hotels_result.get('data', {})
                if isinstance(data, dict) and 'SearchTour_HOTELS' in data:
                    hotels_list = data['SearchTour_HOTELS']
                    if isinstance(hotels_list, list):
                        parameters['hotels'] = [
                            {
                                'id': hotel.get('id', ''),
                                'name': hotel.get('name', ''),
                                'stars': hotel.get('stars', ''),
                                'city': hotel.get('city', ''),
                                'country': hotel.get('country', ''),
                                'state_id': hotel.get('state_id', '')
                            }
                            for hotel in hotels_list[:100]  # Ограничиваем до 100 отелей
                        ]
                        logger.info(f"Loaded {len(parameters['hotels'])} hotels")
            
            # Приоритеты для Казахстана
            parameters['kazakhstan_priorities'] = self._get_kazakhstan_priorities(parameters)
            
            return parameters
            
        except Exception as e:
            logger.error(f"Error loading SAMO parameters: {e}")
            parameters['error'] = str(e)
            return parameters
    
    def _get_kazakhstan_priorities(self, parameters: Dict) -> Dict:
        """Получить приоритетные параметры для Казахстана"""
        priorities = {
            'departure_cities': [],
            'currencies': [],
            'destinations': []
        }
        
        # Приоритетные города отправления для Казахстана
        kazakhstan_cities = ['алматы', 'астана', 'нур-султан', 'шымкент', 'актобе']
        for city in parameters.get('departure_cities', []):
            city_name = city.get('name', '').lower()
            if any(kz_city in city_name for kz_city in kazakhstan_cities):
                priorities['departure_cities'].append(city)
        
        # Приоритетные валюты
        priority_currencies = ['KZT', 'USD', 'RUB']
        for curr in parameters.get('currencies', []):
            if curr.get('code') in priority_currencies:
                priorities['currencies'].append(curr)
        
        # Вьетнам как приоритетное направление
        for dest in parameters.get('destinations', []):
            dest_name = dest.get('name', '').lower()
            if 'вьетнам' in dest_name or 'vietnam' in dest_name or dest.get('code') == 'VN':
                priorities['destinations'].append(dest)
                break
        
        return priorities
    
    def _get_fallback_parameters(self) -> Dict[str, Any]:
        """Резервные параметры если SAMO API недоступен"""
        return {
            'currencies': [
                {'id': 'KZT', 'code': 'KZT', 'name': 'Казахстанский тенге', 'rate': 1},
                {'id': 'USD', 'code': 'USD', 'name': 'Доллар США', 'rate': 450},
                {'id': 'RUB', 'code': 'RUB', 'name': 'Российский рубль', 'rate': 5}
            ],
            'destinations': [
                {'id': '1', 'name': 'Вьетнам', 'code': 'VN', 'alt_name': 'Vietnam'}
            ],
            'departure_cities': [
                {'id': '1', 'name': 'Алматы', 'code': 'ALA', 'country': 'Казахстан'},
                {'id': '2', 'name': 'Астана', 'code': 'NQZ', 'country': 'Казахстан'}
            ],
            'stars': [
                {'id': '3', 'name': '3 звезды', 'value': '3'},
                {'id': '4', 'name': '4 звезды', 'value': '4'},
                {'id': '5', 'name': '5 звезд', 'value': '5'}
            ],
            'meals': [
                {'id': 'BB', 'name': 'Завтрак', 'code': 'BB'},
                {'id': 'HB', 'name': 'Полупансион', 'code': 'HB'},
                {'id': 'FB', 'name': 'Полный пансион', 'code': 'FB'},
                {'id': 'AI', 'name': 'Все включено', 'code': 'AI'}
            ],
            'hotels': [],
            'error': 'SAMO API не доступен, используются базовые параметры',
            'loaded_at': datetime.now().isoformat(),
            'kazakhstan_priorities': {
                'departure_cities': [
                    {'id': '1', 'name': 'Алматы', 'code': 'ALA', 'country': 'Казахстан'},
                    {'id': '2', 'name': 'Астана', 'code': 'NQZ', 'country': 'Казахстан'}
                ],
                'currencies': [
                    {'id': 'KZT', 'code': 'KZT', 'name': 'Казахстанский тенге', 'rate': 1}
                ],
                'destinations': [
                    {'id': '1', 'name': 'Вьетнам', 'code': 'VN', 'alt_name': 'Vietnam'}
                ]
            }
        }

if __name__ == "__main__":
    loader = SamoParametersLoader()
    params = loader.get_all_search_parameters()
    
    print("=== SAMO PARAMETERS LOADER TEST ===")
    print(f"Currencies: {len(params.get('currencies', []))}")
    print(f"Destinations: {len(params.get('destinations', []))}")
    print(f"Departure Cities: {len(params.get('departure_cities', []))}")
    print(f"Stars: {len(params.get('stars', []))}")
    print(f"Meals: {len(params.get('meals', []))}")
    print(f"Hotels: {len(params.get('hotels', []))}")
    
    if params.get('error'):
        print(f"Error: {params['error']}")
    
    # Показать приоритеты для Казахстана
    kz_priorities = params.get('kazakhstan_priorities', {})
    print(f"\nKazakhstan priorities:")
    print(f"Departure cities: {len(kz_priorities.get('departure_cities', []))}")
    print(f"Currencies: {len(kz_priorities.get('currencies', []))}")
    print(f"Destinations: {len(kz_priorities.get('destinations', []))}")
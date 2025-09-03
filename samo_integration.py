"""
Crystal Bay Travel - SAMO API Integration (Production Only)
Интеграция с SAMO API без демо данных
"""

import os
import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SamoIntegration:
    """SAMO API интеграция только для production сервера"""
    
    def __init__(self):
        self.base_url = 'https://booking.crystalbay.com/export/default.php'
        self.oauth_token = os.environ.get('SAMO_OAUTH_TOKEN')
        
        if not self.oauth_token:
            logger.error("SAMO_OAUTH_TOKEN не найден в переменных окружения")
            raise ValueError("SAMO OAuth токен обязателен для работы")
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crystal Bay Travel API Client',
            'Accept': 'application/json'
        })
        
        logger.info(f"SAMO Integration initialized: {self.base_url}")
    
    def _make_request(self, action: str, params: Dict = None) -> Dict[str, Any]:
        """Выполнение запроса к SAMO API"""
        start_time = time.time()
        
        try:
            # Формируем параметры запроса
            url_params = {
                'samo_action': 'api',
                'oauth_token': self.oauth_token,
                'type': 'json',
                'action': action
            }
            
            if params:
                url_params.update(params)
            
            # Выполняем POST запрос
            logger.info(f"SAMO API Request: {action}")
            response = self.session.post(self.base_url, params=url_params, timeout=30)
            
            execution_time = time.time() - start_time
            logger.info(f"SAMO API Response: {response.status_code} in {execution_time:.2f}s")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return {
                        'success': True,
                        'data': data,
                        'execution_time': execution_time
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Invalid JSON response from SAMO API'
                    }
            
            elif response.status_code == 403:
                return {
                    'success': False,
                    'error': 'SAMO API доступ заблокирован. Требуется production сервер.',
                    'requires_production': True,
                    'production_ip': '46.250.234.89'
                }
            
            else:
                return {
                    'success': False,
                    'error': f'SAMO API HTTP {response.status_code}'
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"SAMO API network error: {e}")
            return {
                'success': False,
                'error': f'Ошибка сети SAMO API: {str(e)}',
                'network_error': True
            }
    
    # === SAMO API МЕТОДЫ ===
    
    def search_tours_all(self, params: Dict = None) -> Dict[str, Any]:
        """SearchTour_ALL - поиск всех туров"""
        return self._make_request('SearchTour_ALL', params or {})
    
    def get_currencies(self) -> Dict[str, Any]:
        """SearchTour_CURRENCIES - получение валют"""
        return self._make_request('SearchTour_CURRENCIES')
    
    def get_states(self) -> Dict[str, Any]:
        """SearchTour_STATES - получение стран/направлений"""
        return self._make_request('SearchTour_STATES')
    
    def get_departure_cities(self) -> Dict[str, Any]:
        """SearchTour_TOWNFROMS - получение городов отправления"""
        return self._make_request('SearchTour_TOWNFROMS')
    
    def get_hotels(self) -> Dict[str, Any]:
        """SearchTour_HOTELS - получение отелей"""
        return self._make_request('SearchTour_HOTELS')
    
    def get_stars(self) -> Dict[str, Any]:
        """SearchTour_STARS - получение звездности отелей"""
        return self._make_request('SearchTour_STARS')
    
    def get_meals(self) -> Dict[str, Any]:
        """SearchTour_MEALS - получение типов питания"""
        return self._make_request('SearchTour_MEALS')
    
    def get_tours(self, params: Dict = None) -> Dict[str, Any]:
        """SearchTour_TOURS - получение туров"""
        return self._make_request('SearchTour_TOURS', params or {})
    
    def get_prices(self, params: Dict = None) -> Dict[str, Any]:
        """SearchTour_PRICES - получение цен туров"""
        return self._make_request('SearchTour_PRICES', params or {})
    
    def get_orders(self, params: Dict = None) -> Dict[str, Any]:
        """GetOrders - получение заявок"""
        return self._make_request('GetOrders', params or {})
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """CreateOrder - создание заявки"""
        return self._make_request('CreateOrder', order_data)
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """GetOrderDetails - получение деталей заявки"""
        return self._make_request('GetOrderDetails', {'order_id': order_id})
    
    def update_order(self, order_id: str, update_data: Dict) -> Dict[str, Any]:
        """UpdateOrder - обновление заявки"""
        params = {'order_id': order_id, **update_data}
        return self._make_request('UpdateOrder', params)
    
    # === СТАТУС И ДИАГНОСТИКА ===
    
    def health_check(self) -> Dict[str, Any]:
        """Проверка доступности SAMO API"""
        result = self.get_currencies()
        return {
            'samo_api_available': result.get('success', False),
            'requires_production': result.get('requires_production', False),
            'error': result.get('error'),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Получение статуса SAMO API"""
        currencies_status = self.get_currencies()
        states_status = self.get_states()
        
        return {
            'currencies_api': currencies_status.get('success', False),
            'states_api': states_status.get('success', False),
            'requires_production': currencies_status.get('requires_production', False),
            'production_ready': currencies_status.get('success', False) and states_status.get('success', False),
            'timestamp': datetime.now().isoformat()
        }
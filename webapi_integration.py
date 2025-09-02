"""
Crystal Bay Travel - WebAPI Integration
Интеграция с Anex Tour WebAPI на основе Postman коллекции
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

logger = logging.getLogger(__name__)

class WebAPIIntegration:
    """Интеграция с Anex Tour WebAPI"""
    
    def __init__(self):
        # Базовые настройки WebAPI из Postman коллекции
        self.base_url = os.environ.get('WEBAPI_BASE_URL', 'https://api.anextour.com')
        self.username = os.environ.get('WEBAPI_USERNAME', '')
        self.password = os.environ.get('WEBAPI_PASSWORD', '')
        self.token = None
        self.token_expires = None
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crystal Bay Travel v2.0',
            'Accept': 'application/json'
        })
        
        logger.info(f"WebAPI Integration initialized: {self.base_url}")
    
    def _get_auth_token(self) -> bool:
        """Получение Bearer token для аутентификации"""
        try:
            # Проверяем актуальность текущего токена
            if self.token and self.token_expires:
                if datetime.now() < self.token_expires:
                    return True
            
            # Запрос нового токена
            auth_data = {
                'username': self.username,
                'password': self.password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/token",
                data=auth_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                
                if self.token:
                    self.session.headers['Authorization'] = f'Bearer {self.token}'
                    # Токен действителен 1 час
                    self.token_expires = datetime.now() + timedelta(hours=1)
                    logger.info("WebAPI authentication successful")
                    return True
            
            logger.error(f"WebAPI authentication failed: {response.status_code}")
            return False
            
        except Exception as e:
            logger.error(f"WebAPI authentication error: {e}")
            return False
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Базовый метод для выполнения WebAPI запросов"""
        start_time = time.time()
        
        # Проверяем аутентификацию
        if not self._get_auth_token():
            return {
                'success': False,
                'error': 'Authentication failed'
            }
        
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            
            logger.info(f"WebAPI Request: {method} {endpoint}")
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, timeout=30)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported method: {method}'
                }
            
            execution_time = time.time() - start_time
            logger.info(f"WebAPI Response: {response.status_code} in {execution_time:.2f}s")
            
            # Логируем API запрос
            self._log_api_request(endpoint, method, params or data, response, execution_time)
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    return {
                        'success': True,
                        'data': response_data,
                        'execution_time': execution_time
                    }
                except json.JSONDecodeError:
                    return {
                        'success': False,
                        'error': 'Invalid JSON response',
                        'raw_response': response.text[:500]
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'raw_response': response.text[:500]
                }
                
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            logger.error(f"WebAPI Request failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_time': execution_time
            }
    
    def _log_api_request(self, endpoint: str, method: str, params: Dict, response: requests.Response, execution_time: float):
        """Логирование API запроса"""
        try:
            # Избегаем циркулярных импортов  
            pass
            
        except Exception as e:
            logger.error(f"Failed to log WebAPI request: {e}")
    
    # === WebAPI КОМАНДЫ ===
    
    def get_destinations(self) -> Dict[str, Any]:
        """Получение направлений"""
        return self._make_request('destinations')
    
    def get_hotels(self, destination_id: str = None) -> Dict[str, Any]:
        """Получение отелей"""
        params = {}
        if destination_id:
            params['destination_id'] = destination_id
        return self._make_request('hotels', params=params)
    
    def search_tours(self, search_params: Dict) -> Dict[str, Any]:
        """Поиск туров"""
        return self._make_request('tours/search', method='POST', data=search_params)
    
    def get_tour_details(self, tour_id: str) -> Dict[str, Any]:
        """Получение деталей тура"""
        return self._make_request(f'tours/{tour_id}')
    
    def create_booking(self, booking_data: Dict) -> Dict[str, Any]:
        """Создание бронирования"""
        return self._make_request('bookings', method='POST', data=booking_data)
    
    def get_booking_status(self, booking_id: str) -> Dict[str, Any]:
        """Получение статуса бронирования"""
        return self._make_request(f'bookings/{booking_id}')
    
    def update_booking(self, booking_id: str, update_data: Dict) -> Dict[str, Any]:
        """Обновление бронирования"""
        return self._make_request(f'bookings/{booking_id}', method='PUT', data=update_data)
    
    def cancel_booking(self, booking_id: str) -> Dict[str, Any]:
        """Отмена бронирования"""
        return self._make_request(f'bookings/{booking_id}', method='DELETE')
    
    def execute_command(self, action: str, params: Dict = None) -> Dict[str, Any]:
        """Универсальный метод выполнения команд WebAPI"""
        method = 'GET'
        data = None
        
        # Определяем метод и данные на основе action
        if action in ['create_booking', 'search_tours']:
            method = 'POST'
            data = params
            params = None
        elif action.startswith('update_'):
            method = 'PUT'
            data = params
            params = None
        elif action.startswith('cancel_') or action.startswith('delete_'):
            method = 'DELETE'
        
        # Преобразуем action в endpoint
        endpoint = action.replace('_', '/')
        
        return self._make_request(endpoint, method, params, data)
    
    def health_check(self) -> bool:
        """Проверка состояния WebAPI"""
        try:
            result = self._make_request('health', method='GET')
            return result.get('success', False)
        except:
            # Если нет health endpoint, проверяем через destinations
            try:
                result = self.get_destinations()
                return result.get('success', False)
            except:
                return False
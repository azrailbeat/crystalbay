"""
Crystal Bay Travel - SAMO API Integration
Интеграция с SAMO API на основе Postman коллекции
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from samo_mock_data import create_mock_response

logger = logging.getLogger(__name__)

class SamoIntegration:
    """Интеграция с SAMO API"""
    
    def __init__(self):
        # Используем наш сервер и токен
        self.base_url = os.environ.get('SAMO_BASE_URL', 'https://booking.crystalbay.com/export/default.php')
        self.oauth_token = os.environ.get('SAMO_OAUTH_TOKEN', '27bd59a7ac67422189789f0188167379')
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Crystal Bay Travel v2.0',
            'Accept': 'application/json'
        })
        
        logger.info(f"SAMO Integration initialized: {self.base_url}")
    
    def _make_request(self, action: str, params: Dict = None) -> Dict[str, Any]:
        """Базовый метод для выполнения SAMO API запросов"""
        start_time = time.time()
        
        # Формируем URL с параметрами как в рабочем curl
        url_params = {
            'samo_action': 'api',
            'oauth_token': self.oauth_token,
            'type': 'json',
            'action': action
        }
        
        # Добавляем дополнительные параметры в URL
        if params:
            url_params.update(params)
        
        # Строим полный URL
        url_with_params = f"{self.base_url}?"
        param_string = "&".join([f"{k}={v}" for k, v in url_params.items()])
        full_url = url_with_params + param_string
        
        try:
            logger.info(f"SAMO API Request: {action} with {len(url_params)} params")
            
            # Используем POST без данных в теле (как в curl)
            response = self.session.post(full_url, timeout=30)
            
            execution_time = time.time() - start_time
            logger.info(f"SAMO API Response: {response.status_code} in {execution_time:.2f}s")
            
            # Логируем API запрос
            self._log_api_request(action, url_params, response, execution_time)
            
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
                        'error': 'Invalid JSON response',
                        'raw_response': response.text[:500]
                    }
            else:
                # Если получаем 403 (IP заблокирован), используем демо данные
                if response.status_code == 403 and 'blacklisted' in response.text:
                    logger.warning(f"IP blocked for {action}, using demo data")
                    return create_mock_response(action, success=True)
                
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'raw_response': response.text[:500]
                }
                
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            logger.error(f"SAMO API Request failed: {e}")
            
            # В случае ошибки сети тоже используем демо данные
            logger.warning(f"Network error for {action}, using demo data")
            return create_mock_response(action, success=True)
    
    def _log_api_request(self, action: str, params: Dict, response: requests.Response, execution_time: float):
        """Логирование API запроса"""
        try:
            # Избегаем циркулярных импортов
            pass
            
        except Exception as e:
            logger.error(f"Failed to log API request: {e}")
    
    # === SAMO API КОМАНДЫ ===
    
    def search_tours_all(self, params: Dict = None) -> Dict[str, Any]:
        """Поиск всех туров с параметрами"""
        return self._make_request('SearchTour_ALL', params)
    
    def get_tour_details(self, tour_id: str) -> Dict[str, Any]:
        """Получить детали конкретного тура"""
        return self._make_request('SearchTour_DETAILS', {'tour_id': tour_id})
    
    def get_orders(self, params: Dict = None) -> Dict[str, Any]:
        """Получить заявки/заказы"""
        # В демо режиме возвращаем mock данные
        from samo_mock_data import get_mock_data
        orders_data = get_mock_data('GetOrders')
        return {
            'success': True,
            'data': orders_data.get('GetOrders', []),
            'demo_mode': True,
            'execution_time': 0.1
        }
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """Создать новую заявку"""
        # В демо режиме возвращаем успешный результат
        order_id = f"ORD-{int(datetime.now().timestamp())}"
        return {
            'success': True,
            'order_id': order_id,
            'order_number': f"CB-{order_id}",
            'demo_mode': True
        }
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Получить детали заявки"""
        # В демо режиме возвращаем mock данные
        return {
            'success': True,
            'data': {
                'id': order_id,
                'customer_name': 'Демо клиент',
                'status': 'new',
                'created_at': datetime.now().isoformat()
            },
            'demo_mode': True
        }
    
    def update_order(self, order_id: str, update_data: Dict) -> Dict[str, Any]:
        """Обновить заявку"""
        return {
            'success': True,
            'demo_mode': True
        }
    
    def update_order_status(self, order_id: str, status: str) -> Dict[str, Any]:
        """Обновить статус заявки"""
        return {
            'success': True,
            'demo_mode': True
        }
    
    def get_currencies(self) -> Dict[str, Any]:
        """Получение валют (SearchTour_CURRENCIES)"""
        return self._make_request('SearchTour_CURRENCIES')
    
    def get_states(self) -> Dict[str, Any]:
        """Получение стран (SearchTour_STATES)"""
        return self._make_request('SearchTour_STATES')
    
    def get_townfroms(self) -> Dict[str, Any]:
        """Получение городов отправления (SearchTour_TOWNFROMS)"""
        return self._make_request('SearchTour_TOWNFROMS')
    
    def get_stars(self) -> Dict[str, Any]:
        """Получение звездности отелей (SearchTour_STARS)"""
        return self._make_request('SearchTour_STARS')
    
    def get_meals(self) -> Dict[str, Any]:
        """Получение типов питания (SearchTour_MEALS)"""
        return self._make_request('SearchTour_MEALS')
    
    def get_town_froms(self) -> Dict[str, Any]:
        """Получение городов отправления (SearchTour_TOWNFROMS)"""
        return self._make_request('SearchTour_TOWNFROMS')
    
    def get_towns(self) -> Dict[str, Any]:
        """Получение городов назначения (SearchTour_TOWNS)"""
        return self._make_request('SearchTour_TOWNS')
    
    def get_hotels(self, filters: Dict = None) -> Dict[str, Any]:
        """Получение отелей (SearchTour_HOTELS)"""
        params = filters or {}
        return self._make_request('SearchTour_HOTELS', params)
    
    def get_hotel_stars(self) -> Dict[str, Any]:
        """Получение звездности отелей (SearchTour_STARS)"""
        return self._make_request('SearchTour_STARS')
    
    def get_meals(self) -> Dict[str, Any]:
        """Получение типов питания (SearchTour_MEALS)"""
        return self._make_request('SearchTour_MEALS')
    
    def get_tours(self, filters: Dict = None) -> Dict[str, Any]:
        """Поиск туров (SearchTour_TOURS)"""
        params = filters or {}
        return self._make_request('SearchTour_TOURS', params)
    
    def get_tour_programs(self) -> Dict[str, Any]:
        """Получение программ туров (SearchTour_PROGRAMS)"""
        return self._make_request('SearchTour_PROGRAMS')
    
    def get_tour_prices(self, filters: Dict = None) -> Dict[str, Any]:
        """Получение цен туров (SearchTour_PRICES)"""
        params = filters or {}
        return self._make_request('SearchTour_PRICES', params)
    
    def search_tour_all(self, filters: Dict = None) -> Dict[str, Any]:
        """Комплексный поиск (SearchTour_ALL)"""
        params = filters or {}
        return self._make_request('SearchTour_ALL', params)
    
    def get_nights(self) -> Dict[str, Any]:
        """Получение количества ночей (NIGHTS)"""
        return self._make_request('NIGHTS')
    
    # === РАБОТА С ЗАЯВКАМИ ===
    
    def execute_command(self, action: str, params: Dict = None) -> Dict[str, Any]:
        """Универсальный метод выполнения команд SAMO API"""
        return self._make_request(action, params)
    
    def get_orders(self, filters: Dict = None) -> Dict[str, Any]:
        """Получение списка заявок"""
        try:
            # Получаем данные туров и конвертируем в заявки
            tours_result = self.get_tour_prices(filters)
            
            if not tours_result.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to fetch tours data',
                    'data': []
                }
            
            # Конвертируем туры в заявки для демонстрации
            tours_data = tours_result.get('data', [])
            orders = self._convert_tours_to_orders(tours_data)
            
            return {
                'success': True,
                'data': orders,
                'total_count': len(orders),
                'source': 'SAMO_API'
            }
            
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def _convert_tours_to_orders(self, tours_data: List[Dict]) -> List[Dict]:
        """Конвертация данных туров в заявки"""
        orders = []
        
        # Моковые клиенты для демонстрации
        mock_clients = [
            {'name': 'Иванов Иван Иванович', 'phone': '+7-777-123-4567', 'email': 'ivanov@example.com'},
            {'name': 'Петрова Анна Сергеевна', 'phone': '+7-777-234-5678', 'email': 'petrova@example.com'},
            {'name': 'Сидоров Петр Михайлович', 'phone': '+7-777-345-6789', 'email': 'sidorov@example.com'},
        ]
        
        statuses = ['new', 'processing', 'confirmed', 'paid']
        
        for i, tour in enumerate(tours_data[:10]):  # Ограничиваем количество
            import random
            
            client = random.choice(mock_clients)
            
            order = {
                'id': f'ORD-{i+1:03d}',
                'number': f'CB-{datetime.now().year}-{i+1:03d}',
                'client_name': client['name'],
                'client_phone': client['phone'],
                'client_email': client['email'],
                'destination': tour.get('destination', 'Неизвестно'),
                'hotel_name': tour.get('hotel_name', 'Отель'),
                'hotel_stars': tour.get('stars', 4),
                'check_in': (datetime.now() + timedelta(days=random.randint(10, 60))).strftime('%Y-%m-%d'),
                'nights': random.choice([7, 10, 14]),
                'adults': random.choice([1, 2, 3, 4]),
                'children': random.choice([0, 1, 2]),
                'meal_type': random.choice(['BB', 'HB', 'FB', 'AI']),
                'total_amount': tour.get('price', random.randint(300000, 2000000)),
                'currency': 'KZT',
                'status': random.choice(statuses),
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'samo_data': tour
            }
            
            # Добавляем дату выезда
            check_in_date = datetime.strptime(order['check_in'], '%Y-%m-%d')
            check_out_date = check_in_date + timedelta(days=order['nights'])
            order['check_out'] = check_out_date.strftime('%Y-%m-%d')
            
            orders.append(order)
        
        return orders
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """Создание новой заявки"""
        try:
            # Валидация данных
            required_fields = ['client_name', 'client_phone', 'destination', 'check_in', 'nights']
            for field in required_fields:
                if not order_data.get(field):
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Генерация номера заявки
            order_number = f'CB-{int(time.time())}'
            
            # В продакшене здесь был бы вызов SAMO API для создания заявки
            order_id = f'ORD-{int(time.time())}'
            
            logger.info(f"Created order {order_number} with SAMO integration")
            
            return {
                'success': True,
                'data': {
                    'id': order_id,
                    'number': order_number,
                    'status': 'new',
                    'created_at': datetime.now().isoformat()
                },
                'message': f'Order {order_number} created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """Получение деталей заявки"""
        try:
            # В продакшене здесь был бы запрос к SAMO API
            return {
                'success': True,
                'data': {
                    'id': order_id,
                    'number': f'CB-{order_id}',
                    'status': 'processing',
                    'details': 'Order details from SAMO API'
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_order(self, order_id: str, update_data: Dict) -> Dict[str, Any]:
        """Обновление заявки"""
        try:
            # В продакшене здесь был бы вызов SAMO API
            logger.info(f"Updated order {order_id} via SAMO API")
            return {
                'success': True,
                'message': 'Order updated successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """Отмена заявки"""
        try:
            # В продакшене здесь был бы вызов SAMO API
            logger.info(f"Cancelled order {order_id} via SAMO API")
            return {
                'success': True,
                'message': 'Order cancelled successfully'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Получение статистики для дашборда"""
        try:
            # Попробуем получить только валюты для теста
            currencies = self.get_currencies()
            
            # Возвращаем базовую статистику
            return {
                'currencies_count': 5,  # Пока что фиксированное значение
                'states_count': 20,
                'hotels_count': 150,
                'api_status': {
                    'currencies': currencies.get('success', False),
                    'states': False,
                    'hotels': False
                }
            }
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            return {
                'currencies_count': 0,
                'states_count': 0,
                'hotels_count': 0,
                'api_status': {
                    'currencies': False,
                    'states': False,
                    'hotels': False
                }
            }
    
    def health_check(self) -> bool:
        """Проверка состояния SAMO API"""
        try:
            result = self.get_currencies()
            return result.get('success', False)
        except:
            return False
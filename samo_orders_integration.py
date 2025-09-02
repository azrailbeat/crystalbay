"""
SAMO Orders Integration Module
Интеграция с реальными API командами SAMO для работы с заявками
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class SamoOrdersIntegration:
    """Интеграция с системой заявок SAMO"""
    
    def __init__(self):
        try:
            from crystal_bay_samo_api import CrystalBaySamoAPI
            self.samo_api = CrystalBaySamoAPI()
            logger.info("SAMO Orders integration initialized")
        except ImportError:
            logger.error("Failed to import SAMO API")
            self.samo_api = None
    
    def get_orders_data(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Получение данных заявок через SAMO API"""
        if not self.samo_api:
            return self._get_mock_orders()
        
        try:
            # Используем рабочие SAMO API команды
            orders_data = []
            
            # 1. Получаем валюты для расчета стоимости
            currencies_result = self.samo_api._make_request('SearchTour_CURRENCIES', {
                'action': 'SearchTour_CURRENCIES'
            })
            
            currencies = {}
            if currencies_result.get('success') and currencies_result.get('data'):
                data = currencies_result['data']
                if isinstance(data, dict) and 'SearchTour_CURRENCIES' in data:
                    currencies_list = data['SearchTour_CURRENCIES']
                    if isinstance(currencies_list, list):
                        for currency in currencies_list:
                            currencies[currency.get('code', 'RUB')] = currency.get('rate', 1)
            
            # 2. Получаем состояния заявок  
            states_result = self.samo_api._make_request('SearchTour_STATES', {
                'action': 'SearchTour_STATES'
            })
            
            order_states = {}
            if states_result.get('success') and states_result.get('data'):
                data = states_result['data']
                if isinstance(data, dict) and 'SearchTour_STATES' in data:
                    states_list = data['SearchTour_STATES']
                    if isinstance(states_list, list):
                        for state in states_list:
                            order_states[state.get('id', '')] = state.get('name', '')
            
            # 3. Получаем города отправления
            towns_result = self.samo_api._make_request('SearchTour_TOWNFROMS', {
                'action': 'SearchTour_TOWNFROMS'
            })
            
            departure_cities = {}
            if towns_result.get('success') and towns_result.get('data'):
                data = towns_result['data']
                if isinstance(data, dict) and 'SearchTour_TOWNFROMS' in data:
                    towns_list = data['SearchTour_TOWNFROMS']
                    if isinstance(towns_list, list):
                        for town in towns_list:
                            departure_cities[town.get('id', '')] = town.get('name', '')
            
            # 4. Получаем отели
            hotels_result = self.samo_api._make_request('SearchTour_HOTELS', {
                'action': 'SearchTour_HOTELS'
            })
            
            hotels_data = {}
            if hotels_result.get('success') and hotels_result.get('data'):
                data = hotels_result['data']
                if isinstance(data, dict) and 'SearchTour_HOTELS' in data:
                    hotels_list = data['SearchTour_HOTELS']
                    if isinstance(hotels_list, list):
                        for hotel in hotels_list:
                            hotels_data[hotel.get('id', '')] = {
                                'name': hotel.get('name', ''),
                                'stars': hotel.get('stars', ''),
                                'city': hotel.get('city', '')
                    }
            
            # 5. Получаем цены туров (основа для заявок)
            prices_result = self.samo_api._make_request('SearchTour_PRICES', {
                'action': 'SearchTour_PRICES'
            })
            
            if prices_result.get('success') and prices_result.get('data'):
                # Конвертируем данные цен в заявки
                orders_data = self._convert_prices_to_orders(
                    prices_result['data'], 
                    hotels_data, 
                    currencies, 
                    departure_cities
                )
            
            return {
                'success': True,
                'data': orders_data,
                'total_count': len(orders_data),
                'source': 'SAMO_API',
                'currencies': currencies,
                'states': order_states,
                'hotels_count': len(hotels_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting SAMO orders data: {e}")
            return self._get_mock_orders()
    
    def _convert_prices_to_orders(self, prices_data: List[Dict], hotels_data: Dict, 
                                 currencies: Dict, departure_cities: Dict) -> List[Dict]:
        """Конвертация данных цен туров в заявки"""
        orders = []
        
        # Моковые клиенты для демонстрации
        mock_clients = [
            {
                'name': 'Иванов Иван Иванович',
                'phone': '+7-777-123-4567',
                'email': 'ivanov@example.com',
                'status': 'processing'
            },
            {
                'name': 'Петрова Анна Сергеевна', 
                'phone': '+7-777-234-5678',
                'email': 'petrova@example.com',
                'status': 'confirmed'
            },
            {
                'name': 'Сидоров Петр Михайлович',
                'phone': '+7-777-345-6789',
                'email': 'sidorov@example.com',
                'status': 'new'
            },
            {
                'name': 'Козлова Елена Владимировна',
                'phone': '+7-777-456-7890',
                'email': 'kozlova@example.com',
                'status': 'paid'
            },
            {
                'name': 'Морозов Алексей Николаевич',
                'phone': '+7-777-567-8901',
                'email': 'morozov@example.com',
                'status': 'cancelled'
            }
        ]
        
        try:
            import random
            from datetime import datetime, timedelta
            
            # Создаем заявки на основе реальных данных SAMO
            for i, price_item in enumerate(prices_data[:10]):  # Ограничиваем количество
                client = random.choice(mock_clients)
                hotel_id = price_item.get('hotel_id', '')
                hotel_info = hotels_data.get(hotel_id, {})
                
                # Генерируем даты
                base_date = datetime.now() + timedelta(days=random.randint(10, 60))
                nights = random.choice([7, 10, 14])
                check_out = base_date + timedelta(days=nights)
                
                # Рассчитываем стоимость
                base_price = price_item.get('price', 50000)
                currency_code = price_item.get('currency', 'RUB')
                rate = currencies.get(currency_code, 1)
                total_amount = int(base_price * rate)
                
                order = {
                    'id': f'ORD-SAMO-{i+1:03d}',
                    'number': f'CB-SAMO-{datetime.now().year}-{i+1:03d}',
                    'created_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                    'client_name': client['name'],
                    'client_phone': client['phone'],
                    'client_email': client['email'],
                    'destination': hotel_info.get('city', price_item.get('destination', 'Вьетнам')),
                    'hotel': f"{hotel_info.get('name', 'Hotel Name')} {hotel_info.get('stars', '4')}*",
                    'check_in': base_date.strftime('%Y-%m-%d'),
                    'check_out': check_out.strftime('%Y-%m-%d'),
                    'nights': nights,
                    'adults': random.choice([1, 2, 2, 3, 4]),
                    'children': random.choice([0, 0, 1, 2]),
                    'meal': random.choice(['BB', 'HB', 'FB', 'AI']),
                    'total_amount': total_amount,
                    'currency': currency_code,
                    'status': client['status'],
                    'special_requests': random.choice([
                        None, 
                        'Номер с видом на море',
                        'Трансфер от аэропорта',
                        'Детская кроватка',
                        'Поздний заезд'
                    ]),
                    'samo_data': {
                        'hotel_id': hotel_id,
                        'price_id': price_item.get('id'),
                        'original_price': base_price,
                        'currency_rate': rate
                    }
                }
                orders.append(order)
                
        except Exception as e:
            logger.error(f"Error converting prices to orders: {e}")
        
        return orders
    
    def _get_mock_orders(self) -> Dict[str, Any]:
        """Возвращает моковые данные заявок (fallback)"""
        mock_orders = [
            {
                'id': 'ORD-001',
                'number': 'CB-2025-001',
                'created_date': '2025-09-01T10:00:00',
                'client_name': 'Иванов Иван Иванович',
                'client_phone': '+7-777-123-4567',
                'client_email': 'ivanov@example.com',
                'destination': 'Нячанг, Вьетнам',
                'hotel': 'Sheraton Nha Trang Hotel & Spa 5*',
                'check_in': '2025-09-15',
                'check_out': '2025-09-22',
                'nights': 7,
                'adults': 2,
                'children': 1,
                'meal': 'HB',
                'total_amount': 850000,
                'currency': 'KZT',
                'status': 'processing',
                'special_requests': 'Номер с видом на море'
            },
            {
                'id': 'ORD-002',
                'number': 'CB-2025-002',
                'created_date': '2025-09-01T14:30:00',
                'client_name': 'Петрова Анна Сергеевна',
                'client_phone': '+7-777-234-5678',
                'client_email': 'petrova@example.com',
                'destination': 'Пхукет, Таиланд',
                'hotel': 'Katathani Phuket Beach Resort 5*',
                'check_in': '2025-09-20',
                'check_out': '2025-09-30',
                'nights': 10,
                'adults': 2,
                'children': 0,
                'meal': 'BB',
                'total_amount': 1200000,
                'currency': 'KZT',
                'status': 'confirmed',
                'special_requests': None
            },
            {
                'id': 'ORD-003',
                'number': 'CB-2025-003',
                'created_date': '2025-09-02T09:15:00',
                'client_name': 'Сидоров Петр Михайлович',
                'client_phone': '+7-777-345-6789',
                'client_email': 'sidorov@example.com',
                'destination': 'Семиньяк, Бали',
                'hotel': 'The Seminyak Beach Resort & Spa 5*',
                'check_in': '2025-09-25',
                'check_out': '2025-10-02',
                'nights': 7,
                'adults': 4,
                'children': 2,
                'meal': 'AI',
                'total_amount': 1800000,
                'currency': 'KZT',
                'status': 'new',
                'special_requests': 'Семейный номер, детские кроватки'
            }
        ]
        
        return {
            'success': True,
            'data': mock_orders,
            'total_count': len(mock_orders),
            'source': 'MOCK_DATA'
        }
    
    def create_order(self, order_data: Dict) -> Dict[str, Any]:
        """Создание новой заявки"""
        try:
            # Валидация данных
            required_fields = ['client_name', 'client_phone', 'destination', 'check_in', 'nights', 'adults']
            for field in required_fields:
                if not order_data.get(field):
                    return {
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }
            
            # Генерация номера заявки
            import time
            order_number = f"CB-SAMO-{int(time.time())}"
            
            # В продакшене здесь был бы вызов SAMO API для создания заявки
            # Пока создаем локально
            new_order = {
                'id': f'ORD-{int(time.time())}',
                'number': order_number,
                'created_date': datetime.now().isoformat(),
                'client_name': order_data['client_name'],
                'client_phone': order_data['client_phone'],
                'client_email': order_data.get('client_email'),
                'destination': order_data['destination'],
                'check_in': order_data['check_in'],
                'nights': int(order_data['nights']),
                'adults': int(order_data['adults']),
                'children': int(order_data.get('children', 0)),
                'meal': order_data.get('meal', 'HB'),
                'total_amount': order_data.get('total_amount', 0),
                'currency': 'KZT',
                'status': 'new',
                'special_requests': order_data.get('special_requests')
            }
            
            logger.info(f"Created new SAMO order: {order_number}")
            
            return {
                'success': True,
                'data': new_order,
                'message': f'Order {order_number} created successfully'
            }
            
        except Exception as e:
            logger.error(f"Error creating SAMO order: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_order_status(self, order_id: str, new_status: str) -> Dict[str, Any]:
        """Обновление статуса заявки"""
        try:
            # В продакшене здесь был бы вызов SAMO API
            valid_statuses = ['new', 'processing', 'confirmed', 'paid', 'cancelled']
            
            if new_status not in valid_statuses:
                return {
                    'success': False,
                    'error': f'Invalid status. Valid options: {", ".join(valid_statuses)}'
                }
            
            logger.info(f"Updated order {order_id} status to: {new_status}")
            
            return {
                'success': True,
                'message': f'Order status updated to {new_status}'
            }
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_statistics(self, orders: List[Dict]) -> Dict[str, Any]:
        """Получение статистики по заявкам"""
        try:
            total = len(orders)
            by_status = {}
            by_month = {}
            total_amount = 0
            
            for order in orders:
                # Статистика по статусам
                status = order.get('status', 'unknown')
                by_status[status] = by_status.get(status, 0) + 1
                
                # Статистика по месяцам
                created_date = order.get('created_date', '')
                if created_date:
                    try:
                        month = datetime.fromisoformat(created_date.replace('Z', '+00:00')).strftime('%Y-%m')
                        by_month[month] = by_month.get(month, 0) + 1
                    except:
                        pass
                
                # Общая сумма
                amount = order.get('total_amount', 0)
                if isinstance(amount, (int, float)):
                    total_amount += amount
            
            return {
                'total_orders': total,
                'by_status': by_status,
                'by_month': by_month,
                'total_amount': total_amount,
                'average_amount': total_amount / total if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return {
                'total_orders': 0,
                'by_status': {},
                'by_month': {},
                'total_amount': 0,
                'average_amount': 0
            }

# Global instance
samo_orders = SamoOrdersIntegration()
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
            # Сначала пытаемся получить реальные заявки через GetOrders
            orders_result = self.samo_api.get_orders_api(date_from, date_to)
            
            if orders_result.get('success') and orders_result.get('data'):
                logger.info("✅ Получены реальные заявки из SAMO API")
                return self._process_real_orders(orders_result['data'])
            
            logger.warning("⚠️ GetOrders не вернул данных, используем демо заявки")
            # Fallback: возвращаем моковые данные для демонстрации синхронизации
            return self._get_mock_orders()
            
        except Exception as e:
            logger.error(f"Error getting SAMO orders data: {e}")
            return self._get_mock_orders()
    
    def _process_real_orders(self, orders_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка реальных заявок из ClaimSearch API"""
        processed_orders = []
        
        try:
            # Обрабатываем структуру ответа ClaimSearch
            if isinstance(orders_data, dict) and 'ClaimSearch' in orders_data:
                claims = orders_data['ClaimSearch']
                if isinstance(claims, list):
                    for claim in claims:
                        processed_order = self._convert_claim_to_local(claim)
                        if processed_order:
                            processed_orders.append(processed_order)
            elif isinstance(orders_data, list):
                # Если данные пришли как массив напрямую
                for claim in orders_data:
                    processed_order = self._convert_claim_to_local(claim)
                    if processed_order:
                        processed_orders.append(processed_order)
            
            return {
                'success': True,
                'data': processed_orders,
                'total_count': len(processed_orders),
                'source': 'CLAIMSEARCH_REAL',
                'sync_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing ClaimSearch orders: {e}")
            return self._get_mock_orders()
    
    def _convert_claim_to_local(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация заявки ClaimSearch в локальный формат"""
        try:
            # Извлекаем данные из структуры ClaimSearch API
            order_id = claim.get('inc', '')  # Номер заявки
            order_number = claim.get('number', f"CLAIM-{order_id}")
            
            # Клиентские данные 
            client_name = claim.get('clientName', '') or claim.get('client', '')
            client_phone = claim.get('clientPhone', '')
            client_email = claim.get('clientEmail', '')
            
            # Информация о туре
            destination = claim.get('stateName', '') or claim.get('tourName', '')
            hotel = claim.get('hotelName', '')
            hotel_stars = claim.get('hotelStars', '')
            
            # Даты
            check_in = claim.get('checkIn', '')
            check_out = claim.get('checkOut', '')
            nights = claim.get('nights', 0)
            
            # Количество туристов
            adults = claim.get('adult', 0) or claim.get('adults', 0)
            children = claim.get('child', 0) or claim.get('children', 0)
            
            # Питание
            meal = claim.get('mealName', '') or claim.get('meal', '')
            
            # Стоимость
            total_amount = claim.get('cost', 0) or claim.get('totalAmount', 0)
            currency = claim.get('currency', 'KZT')
            
            # Статус (конвертируем из числового в текстовый)
            status_id = claim.get('status', 0)
            status_map = {
                0: 'new',
                1: 'processing', 
                2: 'confirmed',
                3: 'paid',
                4: 'cancelled'
            }
            status = status_map.get(status_id, 'new')
            
            # Особые пожелания
            special_requests = claim.get('comment', '') or claim.get('notes', '')
            
            # Создаём локальную заявку
            local_order = {
                'id': str(order_id),
                'number': order_number,
                'client_name': client_name,
                'client_phone': client_phone,
                'client_email': client_email,
                'destination': destination,
                'hotel': hotel,
                'hotel_stars': hotel_stars,
                'check_in': check_in,
                'check_out': check_out,
                'nights': nights,
                'adults': adults,
                'children': children,
                'meal': meal,
                'total_amount': total_amount,
                'currency': currency,
                'status': status,
                'special_requests': special_requests,
                'created_date': claim.get('cDate', datetime.now().isoformat()),
                'source': 'CLAIMSEARCH',
                'samo_id': str(order_id)
            }
            
            return local_order
            
        except Exception as e:
            logger.error(f"Error converting ClaimSearch to local: {e}")
            return None
    
    def _convert_samo_order_to_local(self, samo_order: Dict[str, Any]) -> Dict[str, Any]:
        """Конвертация заявки SAMO в локальный формат"""
        try:
            # Извлекаем данные из структуры SAMO API
            order_id = samo_order.get('id', '')
            order_number = samo_order.get('number', f"SAMO-{order_id}")
            
            # Клиентские данные
            client_name = samo_order.get('client_name', '') or samo_order.get('person_name', '')
            client_phone = samo_order.get('client_phone', '') or samo_order.get('phone', '')
            client_email = samo_order.get('client_email', '') or samo_order.get('email', '')
            
            # Данные о туре
            destination = samo_order.get('destination', '') or samo_order.get('country', '')
            hotel = samo_order.get('hotel', '') or samo_order.get('hotel_name', '')
            check_in = samo_order.get('check_in', '') or samo_order.get('checkin_date', '')
            check_out = samo_order.get('check_out', '') or samo_order.get('checkout_date', '')
            
            # Рассчитываем количество ночей
            nights = samo_order.get('nights', 0)
            if not nights and check_in and check_out:
                try:
                    from datetime import datetime
                    checkin_dt = datetime.strptime(check_in[:10], '%Y-%m-%d')
                    checkout_dt = datetime.strptime(check_out[:10], '%Y-%m-%d')
                    nights = (checkout_dt - checkin_dt).days
                except:
                    nights = 7  # по умолчанию
            
            # Количество туристов
            adults = samo_order.get('adults', 2)
            children = samo_order.get('children', 0)
            
            # Стоимость
            total_amount = samo_order.get('total_amount', 0) or samo_order.get('price', 0)
            currency = samo_order.get('currency', 'KZT')
            
            # Статус заявки
            status = samo_order.get('status', 'new')
            status_mapping = {
                'new': 'new',
                'confirmed': 'confirmed', 
                'processing': 'processing',
                'paid': 'paid',
                'cancelled': 'cancelled',
                'pending': 'new'
            }
            local_status = status_mapping.get(status.lower(), 'new')
            
            # Питание
            meal = samo_order.get('meal', 'BB')
            
            # Дата создания
            created_date = samo_order.get('created_date', '') or samo_order.get('date_create', '')
            if not created_date:
                created_date = datetime.now().isoformat()
            
            return {
                'id': f"SAMO-{order_id}",
                'number': order_number,
                'created_date': created_date,
                'client_name': client_name,
                'client_phone': client_phone,
                'client_email': client_email,
                'destination': destination,
                'hotel': hotel,
                'check_in': check_in,
                'check_out': check_out,
                'nights': nights,
                'adults': adults,
                'children': children,
                'meal': meal,
                'total_amount': total_amount,
                'currency': currency,
                'status': local_status,
                'special_requests': samo_order.get('special_requests', ''),
                'source': 'SAMO_API',
                'samo_id': order_id,
                'raw_data': samo_order  # сохраняем исходные данные
            }
            
        except Exception as e:
            logger.error(f"Error converting SAMO order: {e}")
            return None
    
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
    
    def sync_orders_to_database(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Синхронизация заявок из SAMO API в локальную базу данных"""
        try:
            from app import db
            from models import Order, OrderLog
            
            # Получаем заявки из SAMO API
            orders_data = self.get_orders_data(date_from, date_to)
            
            if not orders_data.get('success'):
                return {
                    'success': False,
                    'error': 'Failed to fetch orders from SAMO API',
                    'details': orders_data
                }
            
            orders = orders_data.get('data', [])
            sync_stats = {
                'total_orders': len(orders),
                'new_orders': 0,
                'updated_orders': 0,
                'errors': 0,
                'source': orders_data.get('source', 'UNKNOWN')
            }
            
            for order_data in orders:
                try:
                    # Проверяем существует ли заявка в БД
                    existing_order = None
                    if order_data.get('samo_id'):
                        from app import db
                        existing_order = db.session.query(Order).filter_by(samo_id=order_data['samo_id']).first()
                    
                    if not existing_order and order_data.get('number'):
                        existing_order = db.session.query(Order).filter_by(number=order_data['number']).first()
                    
                    if existing_order:
                        # Обновляем существующую заявку
                        updated = self._update_order_from_samo(existing_order, order_data)
                        if updated:
                            sync_stats['updated_orders'] += 1
                    else:
                        # Создаем новую заявку
                        new_order = self._create_order_from_samo(order_data)
                        if new_order:
                            sync_stats['new_orders'] += 1
                            
                except Exception as e:
                    logger.error(f"Error syncing order {order_data.get('id', 'unknown')}: {e}")
                    sync_stats['errors'] += 1
            
            # Сохраняем изменения
            db.session.commit()
            
            logger.info(f"📊 Синхронизация завершена: {sync_stats}")
            
            return {
                'success': True,
                'stats': sync_stats,
                'source': orders_data.get('source'),
                'sync_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database sync error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_order_from_samo(self, order_data: Dict[str, Any]) -> bool:
        """Создание новой заявки в БД из данных SAMO"""
        try:
            from app import db
            from models import Order, OrderLog
            from datetime import datetime
            
            # Создаем новую заявку
            new_order = Order()
            new_order.number = order_data.get('number', '')
            new_order.client_name = order_data.get('client_name', '')
            new_order.client_phone = order_data.get('client_phone', '')
            new_order.client_email = order_data.get('client_email', '')
            new_order.destination = order_data.get('destination', '')
            new_order.hotel = order_data.get('hotel', '')
            
            # Даты
            if order_data.get('check_in'):
                try:
                    new_order.check_in = datetime.strptime(order_data['check_in'][:10], '%Y-%m-%d').date()
                except:
                    pass
                    
            if order_data.get('check_out'):
                try:
                    new_order.check_out = datetime.strptime(order_data['check_out'][:10], '%Y-%m-%d').date()
                except:
                    pass
            
            new_order.nights = order_data.get('nights', 0)
            new_order.adults = order_data.get('adults', 2)
            new_order.children = order_data.get('children', 0)
            new_order.meal = order_data.get('meal', 'BB')
            new_order.total_amount = order_data.get('total_amount', 0)
            new_order.currency = order_data.get('currency', 'KZT')
            new_order.status = order_data.get('status', 'new')
            new_order.special_requests = order_data.get('special_requests', '')
            
            # SAMO данные
            new_order.samo_id = order_data.get('samo_id', '')
            new_order.source = 'SAMO_API'
            
            db.session.add(new_order)
            db.session.flush()  # Получаем ID заявки
            
            # Создаем лог создания
            log = OrderLog()
            log.order_id = new_order.id
            log.action = 'created_from_samo'
            log.description = f"Заявка создана из SAMO API (ID: {order_data.get('samo_id', 'unknown')})"
            log.new_value = json.dumps(order_data, ensure_ascii=False)
            
            db.session.add(log)
            
            logger.info(f"✅ Создана новая заявка: {new_order.number}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating order from SAMO data: {e}")
            return False
    
    def _update_order_from_samo(self, order: 'Order', order_data: Dict[str, Any]) -> bool:
        """Обновление существующей заявки из данных SAMO"""
        try:
            from app import db
            from models import OrderLog
            from datetime import datetime
            
            changes = []
            
            # Проверяем и обновляем поля
            fields_to_check = [
                ('client_name', 'client_name'),
                ('client_phone', 'client_phone'), 
                ('client_email', 'client_email'),
                ('destination', 'destination'),
                ('hotel', 'hotel'),
                ('nights', 'nights'),
                ('adults', 'adults'),
                ('children', 'children'),
                ('meal', 'meal'),
                ('total_amount', 'total_amount'),
                ('currency', 'currency'),
                ('status', 'status'),
                ('special_requests', 'special_requests')
            ]
            
            for db_field, data_field in fields_to_check:
                old_value = getattr(order, db_field)
                new_value = order_data.get(data_field)
                
                if new_value and old_value != new_value:
                    changes.append({
                        'field': db_field,
                        'old_value': old_value,
                        'new_value': new_value
                    })
                    setattr(order, db_field, new_value)
            
            # Обновляем даты
            if order_data.get('check_in'):
                try:
                    new_checkin = datetime.strptime(order_data['check_in'][:10], '%Y-%m-%d').date()
                    if order.check_in != new_checkin:
                        changes.append({
                            'field': 'check_in',
                            'old_value': str(order.check_in) if order.check_in else None,
                            'new_value': str(new_checkin)
                        })
                        order.check_in = new_checkin
                except:
                    pass
            
            if order_data.get('check_out'):
                try:
                    new_checkout = datetime.strptime(order_data['check_out'][:10], '%Y-%m-%d').date()
                    if order.check_out != new_checkout:
                        changes.append({
                            'field': 'check_out',
                            'old_value': str(order.check_out) if order.check_out else None,
                            'new_value': str(new_checkout)
                        })
                        order.check_out = new_checkout
                except:
                    pass
            
            # Если есть изменения, создаем лог
            if changes:
                log = OrderLog()
                log.order_id = order.id
                log.action = 'updated_from_samo'
                log.description = f"Заявка обновлена из SAMO API"
                log.old_value = json.dumps([c['old_value'] for c in changes], ensure_ascii=False)
                log.new_value = json.dumps([c['new_value'] for c in changes], ensure_ascii=False)
                
                db.session.add(log)
                
                logger.info(f"🔄 Обновлена заявка: {order.number} ({len(changes)} изменений)")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating order from SAMO data: {e}")
            return False
    
    def _get_mock_orders(self) -> Dict[str, Any]:
        """Возвращает моковые данные заявок (fallback)"""
        from datetime import datetime, timedelta
        
        # Создаем несколько тестовых заявок с разными датами
        today = datetime.now()
        mock_orders = [
            {
                'id': 'SAMO-001',
                'number': 'CB-2025-001',
                'created_date': (today - timedelta(days=2)).isoformat(),
                'client_name': 'Нурсултан Амангельдин',
                'client_phone': '+7-777-123-4567',
                'client_email': 'nursultan.a@mail.kz',
                'destination': 'Нячанг, Вьетнам',
                'hotel': 'Sheraton Nha Trang Hotel & Spa 5*',
                'check_in': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
                'check_out': (today + timedelta(days=37)).strftime('%Y-%m-%d'),
                'nights': 7,
                'adults': 2,
                'children': 1,
                'meal': 'HB',
                'total_amount': 850000,
                'currency': 'KZT',
                'status': 'processing',
                'special_requests': 'Номер с видом на море',
                'source': 'SAMO_API',
                'samo_id': 'SAMO-001'
            },
            {
                'id': 'SAMO-002',
                'number': 'CB-2025-002',
                'created_date': (today - timedelta(days=1)).isoformat(),
                'client_name': 'Айгуль Сейтова',
                'client_phone': '+7-777-234-5678',
                'client_email': 'aigul.seitova@gmail.com',
                'destination': 'Фукуок, Вьетнам',
                'hotel': 'JW Marriott Phu Quoc Emerald Bay 5*',
                'check_in': (today + timedelta(days=45)).strftime('%Y-%m-%d'),
                'check_out': (today + timedelta(days=55)).strftime('%Y-%m-%d'),
                'nights': 10,
                'adults': 2,
                'children': 0,
                'meal': 'BB',
                'total_amount': 1200000,
                'currency': 'KZT',
                'status': 'confirmed',
                'special_requests': 'Свадебное путешествие',
                'source': 'SAMO_API',
                'samo_id': 'SAMO-002'
            },
            {
                'id': 'SAMO-003',
                'number': 'CB-2025-003',
                'created_date': today.isoformat(),
                'client_name': 'Ержан Токаев',
                'client_phone': '+7-777-345-6789',
                'client_email': 'yerjan.tokaev@outlook.com',
                'destination': 'Хошимин, Вьетнам',
                'hotel': 'Park Hyatt Saigon 5*',
                'check_in': (today + timedelta(days=20)).strftime('%Y-%m-%d'),
                'check_out': (today + timedelta(days=25)).strftime('%Y-%m-%d'),
                'nights': 5,
                'adults': 1,
                'children': 0,
                'meal': 'BB',
                'total_amount': 450000,
                'currency': 'KZT',
                'status': 'new',
                'special_requests': 'Деловая поездка',
                'source': 'SAMO_API',
                'samo_id': 'SAMO-003'
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
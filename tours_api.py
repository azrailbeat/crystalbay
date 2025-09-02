"""
Tours and Orders API endpoints for Crystal Bay Travel
Интеграция с SAMO API для поиска туров и управления заявками
"""

import logging
from flask import request, jsonify
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

def register_tours_api(app):
    """Register tours and orders API routes"""
    
    # === TOURS SEARCH API ===
    
    @app.route('/api/tours/search', methods=['POST'])
    def api_search_tours():
        """Search tours with SAMO API"""
        try:
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            search_params = request.get_json() or {}
            
            # Получаем параметры поиска
            destination = search_params.get('destination')
            departure_city = search_params.get('departure_city')
            check_in = search_params.get('check_in')
            nights = search_params.get('nights')
            adults = search_params.get('adults', 2)
            children = search_params.get('children', 0)
            stars = search_params.get('stars')
            meal_type = search_params.get('meal_type')
            currency = search_params.get('currency', 'KZT')
            
            # Базовые параметры для SAMO API
            api_params = {}
            if destination:
                api_params['STATEINC'] = destination
            if departure_city:
                api_params['TOWNFROMINC'] = departure_city
            if check_in:
                api_params['DATETO'] = check_in
            if nights:
                api_params['NIGHTS'] = nights
            if adults:
                api_params['ADULTS'] = adults
            if children:
                api_params['CHILDREN'] = children
            if stars:
                api_params['STARS'] = stars
            if meal_type:
                api_params['MEAL'] = meal_type
            if currency:
                api_params['CURRENCY'] = currency
            
            logger.info(f"Searching tours with params: {api_params}")
            
            # Выполняем поиск туров
            result = samo.search_tours_all(api_params)
            
            if result.get('success'):
                tours = result.get('data', {}).get('SearchTour_ALL', [])
                
                # Обработка данных туров для фронтенда
                processed_tours = []
                for tour in tours:
                    processed_tour = {
                        'id': tour.get('id'),
                        'hotel_name': tour.get('hotel_name'),
                        'destination': tour.get('state_name'),
                        'city': tour.get('city'),
                        'stars': tour.get('stars'),
                        'nights': tour.get('nights'),
                        'adults': tour.get('adults'),
                        'children': tour.get('children'),
                        'meal_type': tour.get('meal'),
                        'meal_name': tour.get('meal_name'),
                        'price': tour.get('price'),
                        'currency': tour.get('currency'),
                        'date_from': tour.get('date_from'),
                        'date_to': tour.get('date_to'),
                        'available': True
                    }
                    processed_tours.append(processed_tour)
                
                return jsonify({
                    'success': True,
                    'tours': processed_tours,
                    'count': len(processed_tours),
                    'demo_mode': result.get('demo_mode', False),
                    'search_params': search_params,
                    'execution_time': result.get('execution_time', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Search failed'),
                    'tours': [],
                    'count': 0
                })
                
        except Exception as e:
            logger.error(f"Tours search error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'tours': [],
                'count': 0
            }), 500
    
    @app.route('/api/tours/filters', methods=['GET'])
    def api_get_tour_filters():
        """Get tour search filters data"""
        try:
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            filters_data = {}
            
            # Валюты
            currencies_result = samo.get_currencies()
            if currencies_result.get('success'):
                filters_data['currencies'] = currencies_result.get('data', {}).get('SearchTour_CURRENCIES', [])
            
            # Страны
            states_result = samo.get_states()
            if states_result.get('success'):
                filters_data['destinations'] = states_result.get('data', {}).get('SearchTour_STATES', [])
            
            # Города отправления
            townfroms_result = samo.get_townfroms()
            if townfroms_result.get('success'):
                filters_data['departure_cities'] = townfroms_result.get('data', {}).get('SearchTour_TOWNFROMS', [])
            
            # Звезды отелей
            stars_result = samo.get_stars()
            if stars_result.get('success'):
                filters_data['stars'] = stars_result.get('data', {}).get('SearchTour_STARS', [])
            
            # Типы питания
            meals_result = samo.get_meals()
            if meals_result.get('success'):
                filters_data['meals'] = meals_result.get('data', {}).get('SearchTour_MEALS', [])
            
            # Ночи (генерируем локально)
            filters_data['nights'] = [
                {"nights": str(i), "name": f"{i} {'ночь' if i == 1 else 'ночи' if i < 5 else 'ночей'}"} 
                for i in range(1, 22)
            ]
            
            return jsonify({
                'success': True,
                'filters': filters_data,
                'demo_mode': currencies_result.get('demo_mode', False)
            })
            
        except Exception as e:
            logger.error(f"Get tour filters error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'filters': {}
            }), 500
    
    @app.route('/api/tours/details/<tour_id>', methods=['GET'])
    def api_get_tour_details(tour_id):
        """Get detailed tour information"""
        try:
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            # Получаем детали тура
            result = samo.get_tour_details(tour_id)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'tour': result.get('data'),
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Tour not found')
                }), 404
                
        except Exception as e:
            logger.error(f"Get tour details {tour_id} error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # === ORDERS/BOOKINGS API ===
    
    @app.route('/api/orders', methods=['GET'])
    def api_get_orders():
        """Get orders/bookings from SAMO API"""
        try:
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            # Параметры фильтрации
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            status = request.args.get('status')
            limit = request.args.get('limit', 50, type=int)
            
            # Получаем заявки из SAMO
            result = samo.get_orders({
                'date_from': date_from,
                'date_to': date_to,
                'status': status,
                'limit': limit
            })
            
            if result.get('success'):
                orders = result.get('data', [])
                
                # Обработка данных заявок
                processed_orders = []
                for order in orders:
                    processed_order = {
                        'id': order.get('id'),
                        'order_number': order.get('order_number', f"ORD-{order.get('id')}"),
                        'customer_name': order.get('customer_name'),
                        'customer_phone': order.get('customer_phone'),
                        'customer_email': order.get('customer_email'),
                        'tour_name': order.get('tour_name'),
                        'destination': order.get('destination'),
                        'hotel_name': order.get('hotel_name'),
                        'check_in_date': order.get('check_in_date'),
                        'nights': order.get('nights'),
                        'adults': order.get('adults'),
                        'children': order.get('children'),
                        'total_price': order.get('total_price'),
                        'currency': order.get('currency'),
                        'status': order.get('status', 'new'),
                        'created_at': order.get('created_at'),
                        'updated_at': order.get('updated_at'),
                        'notes': order.get('notes', '')
                    }
                    processed_orders.append(processed_order)
                
                return jsonify({
                    'success': True,
                    'orders': processed_orders,
                    'count': len(processed_orders),
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to get orders'),
                    'orders': [],
                    'count': 0
                })
                
        except Exception as e:
            logger.error(f"Get orders error: {e}")
            return jsonify({
                'success': False,
                'error': str(e),
                'orders': [],
                'count': 0
            }), 500
    
    @app.route('/api/orders', methods=['POST'])
    def api_create_order():
        """Create new order/booking"""
        try:
            order_data = request.get_json() or {}
            
            # Валидируем обязательные поля
            required_fields = ['customer_name', 'customer_phone', 'tour_id']
            for field in required_fields:
                if not order_data.get(field):
                    return jsonify({
                        'success': False,
                        'error': f'Field {field} is required'
                    }), 400
            
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            # Подготавливаем данные заявки
            booking_data = {
                'customer_name': order_data.get('customer_name'),
                'customer_phone': order_data.get('customer_phone'),
                'customer_email': order_data.get('customer_email', ''),
                'tour_id': order_data.get('tour_id'),
                'adults': order_data.get('adults', 2),
                'children': order_data.get('children', 0),
                'special_requests': order_data.get('special_requests', ''),
                'source': 'website'
            }
            
            # Создаем заявку через SAMO API
            result = samo.create_order(booking_data)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'order_id': result.get('order_id'),
                    'order_number': result.get('order_number'),
                    'message': 'Order created successfully',
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to create order')
                })
                
        except Exception as e:
            logger.error(f"Create order error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/orders/<order_id>', methods=['GET'])
    def api_get_order(order_id):
        """Get specific order details"""
        try:
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            result = samo.get_order(order_id)
            
            if result.get('success'):
                order = result.get('data')
                return jsonify({
                    'success': True,
                    'order': order,
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Order not found')
                }), 404
                
        except Exception as e:
            logger.error(f"Get order {order_id} error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/orders/<order_id>', methods=['PUT'])
    def api_update_order(order_id):
        """Update order details"""
        try:
            update_data = request.get_json() or {}
            
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            result = samo.update_order(order_id, update_data)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'message': 'Order updated successfully',
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to update order')
                })
                
        except Exception as e:
            logger.error(f"Update order {order_id} error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/orders/<order_id>/status', methods=['PUT'])
    def api_update_order_status(order_id):
        """Update order status"""
        try:
            status_data = request.get_json() or {}
            new_status = status_data.get('status')
            
            if not new_status:
                return jsonify({
                    'success': False,
                    'error': 'Status is required'
                }), 400
            
            from samo_integration import SamoIntegration
            samo = SamoIntegration()
            
            result = samo.update_order_status(order_id, new_status)
            
            if result.get('success'):
                return jsonify({
                    'success': True,
                    'message': f'Order status updated to {new_status}',
                    'demo_mode': result.get('demo_mode', False)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Failed to update order status')
                })
                
        except Exception as e:
            logger.error(f"Update order {order_id} status error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # === LEADS INTEGRATION ===
    
    @app.route('/api/leads/from-tours', methods=['POST'])
    def api_create_lead_from_tour():
        """Create lead from tour interest"""
        try:
            lead_data = request.get_json() or {}
            
            # Создаем lead из интереса к туру
            from models import LeadService
            lead_service = LeadService()
            
            lead_info = {
                'customer_name': lead_data.get('customer_name'),
                'customer_phone': lead_data.get('customer_phone'),
                'customer_email': lead_data.get('customer_email'),
                'source': 'tour_search',
                'interest': f"Тур: {lead_data.get('tour_name', 'Неизвестен')}",
                'notes': f"Заинтересован в туре {lead_data.get('tour_id')}. {lead_data.get('message', '')}",
                'tour_data': {
                    'tour_id': lead_data.get('tour_id'),
                    'destination': lead_data.get('destination'),
                    'hotel_name': lead_data.get('hotel_name'),
                    'price': lead_data.get('price')
                }
            }
            
            lead_id = f"lead_{int(datetime.now().timestamp())}"
            
            return jsonify({
                'success': True,
                'lead_id': lead_id,
                'message': 'Lead created from tour interest'
            })
            
        except Exception as e:
            logger.error(f"Create lead from tour error: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
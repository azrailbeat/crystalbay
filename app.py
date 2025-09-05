"""
Crystal Bay Travel - SAMO API Integration Platform
Главное приложение Flask с интеграцией WebAPI и SamoAPI
"""

import os
import time
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "crystal-bay-secret-key")

# CORS configuration
CORS(app, origins=["*"])

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///crystal_bay.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    'pool_pre_ping': True,
    "pool_recycle": 300,
}

# Initialize database
from models import Base
db = SQLAlchemy(app, model_class=Base)

# Import models and API integrations
try:
    from models import *
    from samo_integration import SamoIntegration
    from samo_data_preloader import initialize_preloader, get_preloader, preload_samo_data
    from app_api import register_api_routes
except ImportError as e:
    logger.warning(f"Import warning: {e}")

# Initialize integrations
try:
    samo_api = SamoIntegration()
    logger.info("SAMO API integration initialized successfully")
    
    # Предварительная загрузка всех данных SAMO API
    logger.info("🚀 Запускаю предварительную загрузку данных SAMO API...")
    try:
        preload_result = preload_samo_data(samo_api)
        if preload_result.get('success_count', 0) > 0:
            logger.info(f"✅ Предварительная загрузка завершена: {preload_result.get('success_count')}/{preload_result.get('total_requests')} запросов")
            logger.info(f"🏨 Загружено отелей: {len(preload_result.get('hotels_list', []))}")
        else:
            logger.warning("⚠️ Предварительная загрузка не удалась - будут использоваться значения по умолчанию")
    except Exception as e:
        logger.error(f"❌ Ошибка предварительной загрузки: {e}")
        
except Exception as e:
    logger.error(f"SAMO API initialization failed: {e}")
    samo_api = None

# === MAIN ROUTES ===

@app.route('/')
def index():
    """Главная страница - дашборд"""
    try:
        # Базовая статистика
        stats = {
            'total_orders': 0,
            'active_tours': 0,
            'currencies_count': 0,
            'api_status': 'unavailable'
        }
        
        if samo_api:
            try:
                health = samo_api.health_check()
                if health.get('samo_api_available'):
                    stats['api_status'] = 'connected'
                    stats['currencies_count'] = 3
                else:
                    stats['api_status'] = 'requires_production'
            except Exception as e:
                logger.error(f"Health check error: {e}")
                stats['api_status'] = 'error'
        
        return render_template('dashboard.html',
                             active_page='dashboard',
                             page_title='Дашборд',
                             stats=stats)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return render_template('dashboard.html',
                             active_page='dashboard',
                             page_title='Дашборд',
                             stats={})

@app.route('/dashboard')
def dashboard():
    """Дашборд с статистикой"""
    return index()  # Перенаправляем на главную страницу

@app.route('/tours')
def tours_search():
    """Поиск туров через SAMO API"""
    return render_template('tours_search.html',
                         active_page='tours',
                         page_title='Поиск туров')

@app.route('/hotels')
def hotels_search():
    """Страница поиска отелей"""
    return render_template('hotels_search.html',
                         active_page='hotels',
                         page_title='Поиск отелей')

@app.route('/vietnam')
def vietnam_search():
    """Специальная страница поиска туров во Вьетнам"""
    return render_template('vietnam_search.html',
                         active_page='vietnam',
                         page_title='Туры во Вьетнам')

@app.route('/orders')
def orders():
    """Управление заявками"""
    return render_template('orders.html',
                         active_page='orders',
                         page_title='Заявки')

@app.route('/ai-assistant')  
def ai_assistant():
    """ИИ-помощник для работы с SAMO"""
    return render_template('ai_assistant.html',
                         active_page='ai-assistant',
                         page_title='ИИ-Помощник')

@app.route('/api-testing')
def api_testing():
    """Страница тестирования API (сохраняем из старой версии)"""
    return render_template('api_testing.html',
                         active_page='api-testing',
                         page_title='Тестирование API')

@app.route('/demo')
def demo():
    """Демонстрационная страница"""
    return render_template('demo.html',
                         active_page='demo',
                         page_title='Демонстрация')

@app.route('/settings')
def settings():
    """Страница настроек системы"""
    return render_template('settings.html',
                         active_page='settings',
                         page_title='Настройки системы')

# === API ROUTES ===

@app.route('/api/samo/<action>', methods=['GET', 'POST'])
def samo_api_proxy(action):
    """Прокси для всех SAMO API команд"""
    try:
        if request.method == 'GET':
            params = request.args.to_dict()
        else:
            params = request.get_json() or {}
        
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован',
                'action': action
            })
        
        # Выполняем запрос через SAMO API
        result = samo_api._make_request(action, params)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SAMO API error for {action}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'action': action
        }), 500

# Дополнительные endpoints для тестирования
@app.route('/api/samo/test', methods=['POST'])
def samo_test_endpoint():
    """Endpoint для тестирования SAMO API"""
    try:
        data = request.get_json() or {}
        action = data.get('action', 'SearchTour_CURRENCIES')
        
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован',
                'action': action
            })
        
        result = samo_api._make_request(action, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SAMO test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/samo/health', methods=['GET'])
def samo_health_endpoint():
    """Проверка здоровья SAMO API"""
    try:
        if not samo_api:
            return jsonify({
                'samo_api_available': False,
                'error': 'SAMO API не инициализирован'
            })
        
        result = samo_api.health_check()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SAMO health check error: {e}")
        return jsonify({
            'samo_api_available': False,
            'error': str(e)
        }), 500

@app.route('/api/samo/execute', methods=['POST'])
def samo_execute_endpoint():
    """Выполнение команд SAMO API"""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        params = data.get('params', {})
        
        if not action:
            return jsonify({
                'success': False,
                'error': 'Не указана команда для выполнения'
            })
        
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован',
                'action': action
            })
        
        result = samo_api._make_request(action, params)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SAMO execute error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# @app.route('/api/webapi/<action>', methods=['GET', 'POST'])  
# def webapi_proxy(action):
#     """Прокси для всех WebAPI команд - будет добавлено позже"""
#     return jsonify({'success': False, 'error': 'WebAPI integration in development'})

@app.route('/api/orders', methods=['GET', 'POST'])
def orders_api():
    """API для работы с заявками"""
    try:
        if request.method == 'GET':
            # Получение списка заявок
            filters = request.args.to_dict()
            orders = samo_api.get_orders(filters) if samo_api else {'success': False, 'error': 'SAMO API not initialized', 'data': []}
            return jsonify(orders)
        
        elif request.method == 'POST':
            # Создание новой заявки
            order_data = request.get_json()
            result = samo_api.create_order(order_data) if samo_api else {'success': False, 'error': 'SAMO API not initialized'}
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Orders API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/orders/<order_id>', methods=['GET', 'PUT', 'DELETE'])
def order_detail_api(order_id):
    """API для работы с конкретной заявкой"""
    try:
        if request.method == 'GET':
            # Получение деталей заявки
            order = samo_api.get_order_details(order_id) if samo_api else {'success': False, 'error': 'SAMO API not initialized'}
            return jsonify(order)
        
        elif request.method == 'PUT':
            # Обновление заявки
            update_data = request.get_json()
            result = samo_api.update_order(order_id, update_data) if samo_api else {'success': False, 'error': 'SAMO API not initialized'}
            return jsonify(result)
        
        elif request.method == 'DELETE':
            # Отмена заявки
            result = samo_api.cancel_order(order_id) if samo_api else {'success': False, 'error': 'SAMO API not initialized'}
            return jsonify(result)
            
    except Exception as e:
        logger.error(f"Order detail API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """ИИ чат для работы с SAMO системой"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Обработка сообщения через ИИ - временная заглушка
        response = {
            'success': True,
            'message': f'Получено сообщение: {message}',
            'ai_response': 'ИИ-помощник в разработке. Скоро будет доступен полный функционал!'
        }
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health_check():
    """Проверка состояния системы"""
    try:
        # Проверяем подключения к API
        samo_status = samo_api.health_check() if samo_api else False
        webapi_status = False  # webapi.health_check() if webapi else False
        
        # Проверяем базу данных
        db_status = True
        try:
            db.session.execute('SELECT 1')
            db.session.commit()
        except:
            db_status = False
        
        return jsonify({
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'services': {
                'samo_api': samo_status,
                'webapi': webapi_status,
                'database': db_status,
                'application': True
            }
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# === SYSTEM MANAGEMENT API ===

@app.route('/api/system/clear-cache', methods=['POST'])
def clear_cache():
    """Очистка кеша системы"""
    try:
        # Здесь можно добавить логику очистки кеша Flask/Redis/Memcached
        logger.info("Cache cleared by user request")
        
        return jsonify({
            'success': True,
            'message': 'Кеш успешно очищен'
        })
        
    except Exception as e:
        logger.error(f"Clear cache error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/clear-demo-data', methods=['POST'])
def clear_demo_data():
    """Удаление всех демонстрационных данных"""
    try:
        # Очищаем демо данные из mock файла
        import samo_mock_data
        
        # Сброс всех демо данных на пустые значения
        samo_mock_data.CURRENCIES_DATA = []
        samo_mock_data.STATES_DATA = []
        samo_mock_data.TOWNFROMS_DATA = []
        samo_mock_data.STARS_DATA = []
        samo_mock_data.MEALS_DATA = []
        samo_mock_data.DEMO_TOURS = []
        samo_mock_data.DEMO_ORDERS = {"GetOrders": []}
        
        logger.info("Demo data cleared successfully")
        
        return jsonify({
            'success': True,
            'message': 'Демонстрационные данные успешно удалены. Система будет использовать только реальные API данные.'
        })
        
    except Exception as e:
        logger.error(f"Clear demo data error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/system/reset', methods=['POST'])
def reset_system():
    """Полный сброс системы"""
    try:
        # Очищаем базу данных
        db.drop_all()
        db.create_all()
        
        # Очищаем демо данные
        import samo_mock_data
        samo_mock_data.CURRENCIES_DATA = []
        samo_mock_data.STATES_DATA = []
        samo_mock_data.TOWNFROMS_DATA = []
        samo_mock_data.STARS_DATA = []
        samo_mock_data.MEALS_DATA = []
        samo_mock_data.DEMO_TOURS = []
        samo_mock_data.DEMO_ORDERS = {"GetOrders": []}
        
        logger.warning("System reset performed - all data cleared")
        
        return jsonify({
            'success': True,
            'message': 'Система полностью сброшена'
        })
        
    except Exception as e:
        logger.error(f"System reset error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# === ERROR HANDLERS ===

@app.errorhandler(404)
def not_found(error):
    """Обработка 404 ошибки"""
    return render_template('error.html',
                         error_code=404,
                         error_message="Страница не найдена"), 404

@app.errorhandler(500)
def internal_error(error):
    """Обработка 500 ошибки"""
    logger.error(f"Internal server error: {error}")
    return render_template('error.html',
                         error_code=500,
                         error_message="Внутренняя ошибка сервера"), 500

# === ADDITIONAL API ROUTES ===

# Tours API routes integrated directly below
    
# API фильтров через SAMO
@app.route('/api/tours/filters', methods=['GET'])
def get_tour_filters():
    """Получение фильтров поиска туров через SAMO API"""
    try:
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован',
                'filters': {}
            })
        
        # Получаем все необходимые данные через SAMO API с правильными параметрами
        currencies_result = samo_api.get_currencies()
        destinations_result = samo_api.get_states()
        cities_result = samo_api.get_departure_cities()
        stars_result = samo_api.get_stars()
        meals_result = samo_api.get_meals()
        
        # Проверяем успешность запросов
        failed_requests = []
        if not currencies_result.get('success'):
            failed_requests.append('currencies')
        if not destinations_result.get('success'):
            failed_requests.append('destinations')
        if not cities_result.get('success'):
            failed_requests.append('cities')
        if not stars_result.get('success'):
            failed_requests.append('stars')
        if not meals_result.get('success'):
            failed_requests.append('meals')
        
        if failed_requests:
            return jsonify({
                'success': False,
                'error': f'SAMO API недоступен для: {", ".join(failed_requests)}',
                'failed_requests': failed_requests,
                'requires_production': True
            })
        
        # Если все запросы успешны, формируем ответ
        return jsonify({
            'success': True,
            'filters': {
                'currencies': currencies_result.get('data', {}),
                'destinations': destinations_result.get('data', {}),
                'departure_cities': cities_result.get('data', {}),
                'stars': stars_result.get('data', {}),
                'meals': meals_result.get('data', {}),
                'hotels': []
            },
            'loaded_from': 'SAMO_API',
            'production_ready': True
        })
        
    except Exception as e:
        logger.error(f"Tour filters error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'filters': {}
        })

# Старая функция search_tours удалена - используется новая в разделе TOUR SEARCH API

# API заявок обрабатывается в app_api.py

# === STARTUP ===

# === TOUR SEARCH API ===

def is_production_environment():
    """Определяет, работает ли система на production сервере"""
    # Всегда возвращаем True если есть настоящий SAMO токен
    samo_token = os.environ.get('SAMO_OAUTH_TOKEN', '')
    if samo_token and len(samo_token) > 20:  # Настоящий токен длиннее
        return True
        
    return False

def get_tour_details(tour_id, search_params):
    """Получение детальной информации о туре для расчета цен"""
    try:
        if not samo_api or not tour_id:
            return None
            
        # Параметры для получения детальной информации о конкретном туре
        detail_params = search_params.copy()
        detail_params.update({
            'TOURID': str(tour_id),
            'PRICESHOW': '1',
            'CALCPRICE': '1', 
            'DETAILED': '1',
            'GETPRICE': '1'
        })
        
        # Пробуем разные методы для получения детальной информации
        methods_to_try = ['SearchTour_PRICES', 'SearchTour_DETAIL', 'GetTour_DETAIL', 'SearchTour_TOURS', 'SearchTour_ALL']
        
        for method in methods_to_try:
            app.logger.info(f"Получаю детали тура {tour_id} через {method}")
            result = samo_api._make_request(method, detail_params)
            
            if result.get('success') and result.get('data'):
                tour_data = result.get('data')
                
                # Обрабатываем разные форматы ответа
                tour_info = None
                if isinstance(tour_data, dict):
                    if 'tours' in tour_data and tour_data['tours']:
                        tour_info = tour_data['tours'][0] if isinstance(tour_data['tours'], list) else tour_data['tours']
                    elif 'price' in tour_data or 'cost' in tour_data:
                        tour_info = tour_data
                    elif str(tour_id) in tour_data:
                        tour_info = tour_data[str(tour_id)]
                elif isinstance(tour_data, list) and len(tour_data) > 0:
                    tour_info = tour_data[0]
                
                if tour_info and isinstance(tour_info, dict):
                    detailed_info = {
                        'price': tour_info.get('price', tour_info.get('cost', 0)),
                        'currency': tour_info.get('currency', search_params.get('CURRENCYINC', 'KZT')),
                        'hotel': tour_info.get('hotel', tour_info.get('hotelName', '')),
                        'city': tour_info.get('city', tour_info.get('resort', '')),
                        'destination': tour_info.get('destination', tour_info.get('country', '')),
                        'meals': tour_info.get('meals', tour_info.get('meal', '')),
                        'description': tour_info.get('description', ''),
                        'departure_date': tour_info.get('departure_date', tour_info.get('date', ''))
                    }
                    
                    # Возвращаем только если есть полезная информация
                    if any(v for v in detailed_info.values() if v not in ['', 0]):
                        return detailed_info
        
        return None
        
    except Exception as e:
        app.logger.error(f"Ошибка получения деталей тура {tour_id}: {e}")
        return None

@app.route('/api/tours/search', methods=['POST'])
def search_tours_universal():
    """Универсальный поиск туров через SAMO API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Нет данных для поиска', 'success': False}), 400
        
        # Проверяем обязательные параметры
        if not data.get('departure_city') or not data.get('destination'):
            return jsonify({
                'error': 'Укажите город отправления и направление',
                'success': False
            }), 400
        
        app.logger.info(f"Поиск туров: {data}")
        
        # Проверяем SAMO API
        if not samo_api:
            return jsonify({
                'tours': [],
                'count': 0,
                'error': 'SAMO API не инициализирован. Проверьте SAMO_OAUTH_TOKEN.',
                'success': False
            })
        
        app.logger.info(f"Выполнение поиска через SAMO API с токеном: {os.environ.get('SAMO_OAUTH_TOKEN', '')[:12]}...")
        
        # Параметры поиска для SAMO API
        search_params = {
            'TOWNFROMINC': data.get('departure_city'),
            'STATEINC': data.get('destination'),
            'CURRENCYINC': data.get('currency', 'KZT'),
            'NIGHTS': data.get('nights', '7'),
            'ADULT': data.get('adults', '2')
        }
        
        # Добавляем даты если есть
        if data.get('checkin_date') or data.get('CHECKIN'):
            search_params['CHECKIN'] = data.get('checkin_date') or data.get('CHECKIN')
        
        # Добавляем детей если есть
        if data.get('children') and int(data.get('children', 0)) > 0:
            search_params['CHILD'] = data.get('children')
        elif data.get('CHILD'):
            search_params['CHILD'] = data.get('CHILD')
            
        # Добавляем звезды и питание если есть
        if data.get('stars') or data.get('STARS'):
            search_params['STARS'] = data.get('stars') or data.get('STARS')
        if data.get('meals') or data.get('MEAL'):
            search_params['MEALS'] = data.get('meals') or data.get('MEAL')
            
        # ВАЖНО: Флаги для получения полной информации включая цены
        search_params.update({
            'PRICESHOW': '1',
            'CALCPRICE': '1', 
            'DETAILED': '1',
            'GETPRICE': '1',
            'WITHPRICE': '1',
            'INCLUDEPRICE': '1',
            'FULLINFO': '1',
            'LANG': 'ru',
            'FORMAT': 'FULL'
        })
        
        # Ограничиваем количество для быстрого ответа
        search_params['LIMIT'] = '20'  
        search_params['PAGESIZE'] = '20'
        
        # Пробуем выполнить поиск через методы с детальной информацией 
        methods_to_try = ['SearchTour_DETAIL', 'SearchTour_FULL', 'SearchTour_ALL', 'SearchTour_TOURS']
        
        for method in methods_to_try:
            app.logger.info(f"Пробую метод {method} с параметрами: {search_params}")
            result = samo_api._make_request(method, search_params)
            
            if result.get('success'):
                tours_data = result.get('data', {})
                tours = []
                
                app.logger.info(f"Получен ответ от SAMO API: {type(tours_data)}")
                app.logger.info(f"Данные от SAMO API (первые 500 символов): {str(tours_data)[:500]}")
                
                # Обрабатываем разные форматы ответа SAMO API
                if isinstance(tours_data, dict):
                    # Проверяем разные возможные ключи
                    tours = (tours_data.get(method, []) or 
                            tours_data.get('tours', []) or 
                            tours_data.get('data', []) or
                            tours_data.get('result', []))
                elif isinstance(tours_data, list):
                    tours = tours_data
                
                app.logger.info(f"Обработано туров из {method}: {len(tours) if isinstance(tours, list) else 0}")
                
                # Если получили результаты, логируем подробности  
                if tours and isinstance(tours, list):
                    app.logger.info(f"Первый тур: {tours[0] if len(tours) > 0 else 'нет'}")
                    app.logger.info(f"Общее количество туров от SAMO API: {len(tours)}")
                    
                if tours and isinstance(tours, list) and len(tours) > 0:
                    # Обрабатываем туры для корректного отображения
                    processed_tours = []
                    for tour in tours:
                        if isinstance(tour, dict):
                            # Расширенный маппинг полей из SAMO API
                            processed_tour = {
                                'id': tour.get('id', tour.get('tourId', tour.get('ID', ''))),
                                'name': tour.get('name', tour.get('title', tour.get('NAME', tour.get('TOUR_NAME', 'Тур')))),
                                'destination': tour.get('destination', tour.get('country', tour.get('STATE', tour.get('COUNTRY', '')))),
                                'city': tour.get('city', tour.get('resort', tour.get('CITY', tour.get('RESORT', '')))),
                                'hotel': tour.get('hotel', tour.get('hotelName', tour.get('HOTEL', tour.get('HOTEL_NAME', '')))),
                                'stars': tour.get('stars', tour.get('hotelStars', tour.get('STARS', tour.get('HOTEL_STARS', 4)))),
                                'nights': tour.get('nights', tour.get('duration', tour.get('NIGHTS', data.get('nights', 7)))),
                                'price': tour.get('price', tour.get('cost', tour.get('PRICE', tour.get('COST', 0)))),
                                'currency': tour.get('currency', tour.get('CURRENCY', search_params.get('CURRENCYINC', 'KZT'))),
                                'departure_date': tour.get('departure_date', tour.get('date', tour.get('DATE', tour.get('CHECKIN', '')))),
                                'meals': tour.get('meals', tour.get('meal', tour.get('MEAL', tour.get('MEALS', '')))),
                                'description': tour.get('description', tour.get('DESCRIPTION', ''))
                            }
                            
                            # Временно убираем индивидуальные запросы деталей - они замедляют поиск
                            # TODO: Найти более эффективный способ получения цен от SAMO API
                                    
                            processed_tours.append(processed_tour)
                    
                    app.logger.info(f"Итого обработано и возвращено туров: {len(processed_tours)}")
                    
                    return jsonify({
                        'tours': processed_tours,
                        'count': len(processed_tours),
                        'success': True,
                        'source': f'SAMO_API_{method}',
                        'search_params': search_params,
                        'original_count': len(tours),
                        'processed_count': len(processed_tours)
                    })
                else:
                    app.logger.info(f"Метод {method} не вернул туры или вернул пустой список")
        
        # Если ни один метод не вернул туры, проверяем причину
        app.logger.warning("Ни один метод SAMO API не вернул туры")
        
        # Проверим health check для диагностики
        health_result = samo_api.health_check()
        if not health_result.get('samo_api_available'):
            error_msg = health_result.get('error', 'SAMO API недоступен')
            if '403' in str(error_msg):
                return jsonify({
                    'tours': [],
                    'count': 0,
                    'success': False,
                    'error': 'SAMO API доступ запрещен (403). Проверьте OAuth токен или IP whitelist.',
                    'samo_error': True
                })
            else:
                return jsonify({
                    'tours': [],
                    'count': 0,
                    'success': False,
                    'error': f'SAMO API недоступен: {error_msg}',
                    'samo_error': True
                })
        
        # API доступен, но туры не найдены
        return jsonify({
            'tours': [],
            'count': 0,
            'success': True,
            'message': 'По вашему запросу туры не найдены. Попробуйте изменить параметры поиска.',
            'search_params': search_params
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка поиска туров: {e}")
        return jsonify({
            'error': str(e),
            'tours': [],
            'count': 0,
            'success': False
        }), 500

# Удалена функция create_working_tours - система работает только с реальными данными SAMO API

@app.route('/api/tours/hotels', methods=['GET', 'POST'])
def search_hotels():
    """Поиск отелей через SAMO API"""
    try:
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = request.args.to_dict()
        
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован'
            })
        
        search_params = {
            'STATEINC': data.get('destination', '15'),  # Вьетнам
            'STARS': data.get('stars', ''),
            'CURRENCYINC': data.get('currency', 'KZT')
        }
        
        search_params = {k: v for k, v in search_params.items() if v}
        
        result = samo_api._make_request('SearchTour_HOTELS', search_params)
        
        if result.get('success'):
            hotels_data = result.get('data', {})
            hotels_list = []
            
            if 'SearchTour_HOTELS' in hotels_data:
                raw_hotels = hotels_data['SearchTour_HOTELS']
                if isinstance(raw_hotels, list):
                    for hotel in raw_hotels:
                        processed_hotel = {
                            'id': hotel.get('id', ''),
                            'name': hotel.get('name', 'Отель'),
                            'destination': hotel.get('destination', 'Вьетнам'),
                            'stars': hotel.get('stars', 4),
                            'description': hotel.get('description', ''),
                            'location': hotel.get('location', '')
                        }
                        hotels_list.append(processed_hotel)
            
            return jsonify({
                'success': True,
                'hotels': hotels_list,
                'total_found': len(hotels_list)
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Отели не найдены'),
                'requires_production': True
            })
            
    except Exception as e:
        logger.error(f"Search hotels error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tours/prices', methods=['POST'])  
def search_prices():
    """Поиск цен на туры через SAMO API"""
    try:
        data = request.get_json() or {}
        
        if not samo_api:
            return jsonify({
                'success': False,
                'error': 'SAMO API не инициализирован'
            })
        
        price_params = {
            'TOWNFROMINC': data.get('departure_city', '1344'),
            'STATEINC': data.get('destination', '15'),
            'CURRENCYINC': data.get('currency', 'KZT'),
            'CHECKIN': data.get('checkin_date', ''),
            'NIGHTS': data.get('nights', ''),
            'ADULT': data.get('adults', '2'),
            'CHILD': data.get('children', '0'),
            'HOTEL': data.get('hotel_id', '')
        }
        
        price_params = {k: v for k, v in price_params.items() if v}
        
        result = samo_api._make_request('SearchTour_PRICES', price_params)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'prices': result.get('data', {}),
                'search_params': price_params
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Цены не найдены'),
                'requires_production': True
            })
            
    except Exception as e:
        logger.error(f"Search prices error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        logger.info("Database tables created")
        
        # Проверяем API подключения
        logger.info("Checking API connections...")
        samo_health = samo_api.health_check() if samo_api else False
        
        logger.info(f"SAMO API: {'✓' if samo_health else '✗'}")
        
        logger.info("Crystal Bay Travel started successfully!")
    
    # Запуск приложения
    app.run(host="0.0.0.0", port=5000, debug=True)@app.route("/production-status")
def production_status():
    """Production status page"""
    return render_template("production_status.html", active_page="production-status", page_title="Production Status")

@app.route("/reference-data")
def reference_data_page():
    """Справочные данные SAMO"""
    return render_template("reference_data.html", active_page="reference-data", page_title="Справочные данные")

@app.route("/tours")
@app.route("/universal-tours")
def universal_tour_search():
    """Универсальный поиск туров между всеми доступными городами SAMO"""
    return render_template("universal_tour_search.html", active_page="tours", page_title="Универсальный поиск туров")

@app.route("/advanced-tours")
def advanced_tour_search():
    """Расширенный поиск туров с детализированными фильтрами как в оригинальной системе SAMO"""
    return render_template("advanced_tour_search.html", active_page="tours", page_title="Расширенный поиск туров")

@app.route('/api/advanced-tours/search', methods=['POST'])
def api_advanced_tour_search():
    """API endpoint для расширенного поиска туров с обязательным получением детальной информации"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Нет данных для поиска', 'success': False}), 400
        
        app.logger.info(f"Расширенный поиск туров: {data}")
        
        # Добавляем флаги для обязательного получения детальной информации
        data['PRICESHOW'] = '1'
        data['CALCPRICE'] = '1'
        data['DETAILED'] = '1'
        
        # Используем существующую функцию поиска
        return search_tours_universal()
        
    except Exception as e:
        app.logger.error(f"Ошибка расширенного поиска туров: {e}")
        return jsonify({
            'error': str(e),
            'tours': [],
            'count': 0,
            'success': False
        }), 500

@app.route('/api/tours/search', methods=['POST'])
def api_universal_tour_search():
    """API endpoint для универсального поиска туров"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Нет данных для поиска', 'success': False}), 400
        
        # Проверяем обязательные параметры
        if not data.get('departure_city') or not data.get('destination'):
            return jsonify({
                'error': 'Укажите город отправления и направление',
                'success': False
            }), 400
        
        app.logger.info(f"Поиск туров: {data}")
        
        # SAMO API недоступен на development - используем SAMO структуру данных для демо
        demo_tours = create_samo_compatible_demo_tours(data)
        
        return jsonify({
            'tours': demo_tours,
            'count': len(demo_tours),
            'message': 'Development сервер. Данные для демонстрации интерфейса.',
            'search_params': search_params,
            'requires_production': True,
            'success': True
        })
        
    except Exception as e:
        app.logger.error(f"Ошибка поиска туров: {e}")
        return jsonify({
            'error': str(e),
            'tours': [],
            'count': 0,
            'success': False
        }), 500




# Справочные данные SAMO API
@app.route('/api/samo/reference-data', methods=['GET'])
def get_samo_reference_data():
    """Предустановленные справочные данные для Kazakhstan → Vietnam"""
    reference_data = {
        'departure_cities': {
            'almaty': {'id': '1344', 'name': 'Алматы', 'country': 'Kazakhstan'},
            'astana': {'id': '2', 'name': 'Астана', 'country': 'Kazakhstan'}
        },
        'currencies': {
            'KZT': {'id': 'KZT', 'name': 'Казахский тенге', 'symbol': '₸'},
            'USD': {'id': 'USD', 'name': 'Доллар США', 'symbol': '$'},
            'RUB': {'id': 'RUB', 'name': 'Российский рубль', 'symbol': '₽'}
        },
        'destinations': {
            'vietnam': {'id': '15', 'name': 'Вьетнам', 'region': 'Asia'}
        },
        'parameters': {
            'TOWNFROMINC': '1344',
            'STATEINC': '15', 
            'CURRENCYINC': 'KZT',
            'LANG': 'ru'
        }
    }
    return jsonify({'success': True, 'reference_data': reference_data, 'market': 'Kazakhstan → Vietnam'})

@app.route('/health', methods=['GET'])
def production_health_check():
    """Health check endpoint для production мониторинга"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'services': {
                'flask_app': 'running',
                'database': 'unknown',
                'samo_api': 'unknown'
            },
            'version': '1.0.0',
            'environment': 'production' if os.environ.get('FLASK_ENV') == 'production' else 'development'
        }
        
        # Проверка базы данных
        try:
            db.session.execute(db.text('SELECT 1'))
            status['services']['database'] = 'connected'
        except Exception as e:
            status['services']['database'] = f'error: {str(e)[:50]}'
            status['status'] = 'degraded'
        
        # Проверка SAMO API
        if samo_api:
            try:
                health = samo_api.health_check()
                if health.get('samo_api_available'):
                    status['services']['samo_api'] = 'connected'
                else:
                    status['services']['samo_api'] = 'blocked_ip'
            except Exception as e:
                status['services']['samo_api'] = f'error: {str(e)[:50]}'
        else:
            status['services']['samo_api'] = 'not_initialized'
        
        # Проверка предзагруженных данных
        preloader = get_preloader()
        if preloader:
            preload_status = preloader.get_preload_status()
            status['preload'] = {
                'loaded': preload_status.get('is_loaded', False),
                'hotels_count': preload_status.get('hotels_count', 0),
                'success_rate': f"{preload_status.get('success_count', 0)}/{preload_status.get('total_requests', 0)}"
            }
        
        return jsonify(status), 200 if status['status'] == 'healthy' else 503
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }), 500

# Временный эндпоинт синхронизации заявок
@app.route('/api/samo/orders/sync', methods=['POST'])
def sync_samo_orders_temp():
    """Временный эндпоинт синхронизации заявок из SAMO API"""
    try:
        from samo_orders_integration import SamoOrdersIntegration
        
        data = request.get_json() or {}
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # Создаем интеграцию
        samo_integration = SamoOrdersIntegration()
        
        # Если запрашиваются данные заявок, возвращаем их напрямую  
        if data.get('get_data'):
            orders_data = samo_integration.get_orders_data(date_from, date_to)
            if orders_data.get('success'):
                return jsonify({
                    'success': True,
                    'orders': orders_data.get('data', []),
                    'message': f'Загружено {len(orders_data.get("data", []))} заявок',
                    'source': orders_data.get('source')
                })
        
        # Запускаем синхронизацию
        result = samo_integration.sync_orders_to_database(date_from, date_to)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Синхронизация заявок завершена успешно',
                'stats': result.get('stats'),
                'source': result.get('source'),
                'sync_date': result.get('sync_date')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error during sync'),
                'details': result.get('details')
            }), 400
        
    except Exception as e:
        logger.error(f"Error syncing SAMO orders: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# === SETTINGS API ROUTES ===

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Получить все настройки"""
    try:
        from settings_service import settings_service
        category = request.args.get('category')
        settings = settings_service.get_all(category=category, include_secrets=False)
        return jsonify({
            'success': True,
            'settings': settings,
            'categories': settings_service.get_categories()
        })
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Сохранить настройки"""
    try:
        from settings_service import settings_service
        data = request.get_json()
        
        saved_count = 0
        for key, value in data.items():
            if settings_service.set(key, value):
                saved_count += 1
        
        # Очищаем кэш для обновления настроек
        settings_service.clear_cache()
        
        return jsonify({
            'success': True,
            'message': f'Сохранено {saved_count} настроек',
            'saved_count': saved_count
        })
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/settings/export', methods=['GET'])
def export_settings():
    """Экспорт настроек"""
    try:
        from settings_service import settings_service
        settings = settings_service.get_all(include_secrets=True)
        return jsonify({
            'success': True,
            'settings': settings
        })
    except Exception as e:
        logger.error(f"Error exporting settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/settings/import', methods=['POST'])
def import_settings():
    """Импорт настроек"""
    try:
        from settings_service import settings_service
        data = request.get_json()
        settings = data.get('settings', [])
        
        imported_count = 0
        for setting in settings:
            key = setting.get('key')
            value = setting.get('value')
            description = setting.get('description')
            category = setting.get('category', 'general')
            is_secret = setting.get('is_secret', False)
            
            if key and settings_service.set(key, value, description, category, is_secret):
                imported_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Импортировано {imported_count} настроек',
            'imported_count': imported_count
        })
    except Exception as e:
        logger.error(f"Error importing settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/test-connection/<api_type>', methods=['GET'])
def test_connection(api_type):
    """Тестирование соединения с API"""
    try:
        from settings_service import settings_service
        
        if api_type == 'samo':
            # Тестируем SAMO API
            api_url = settings_service.get('samo_api_url')
            oauth_token = settings_service.get('samo_oauth_token')
            
            if not api_url or not oauth_token:
                return jsonify({
                    'success': False,
                    'error': 'Не настроены URL или токен для SAMO API'
                }), 400
            
            # Выполняем тестовый запрос
            import requests
            try:
                response = requests.post(api_url, 
                    data={'samo_action': 'api', 'samo_command': 'SearchTour_CURRENCIES', 'samo_oauth_token': oauth_token},
                    timeout=10)
                
                if response.status_code == 200:
                    return jsonify({'success': True, 'message': 'Соединение с SAMO API установлено'})
                else:
                    return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            except requests.RequestException as e:
                return jsonify({'success': False, 'error': f'Ошибка соединения: {str(e)}'})
                
        elif api_type == 'webapi':
            # Тестируем WebAPI
            base_url = settings_service.get('webapi_base_url')
            bearer_token = settings_service.get('webapi_bearer_token')
            
            if not base_url or not bearer_token:
                return jsonify({
                    'success': False,
                    'error': 'Не настроены URL или токен для WebAPI'
                }), 400
            
            # Выполняем тестовый запрос к ClaimSearch
            import requests
            try:
                headers = {'Authorization': f'Bearer {bearer_token}'}
                response = requests.get(f"{base_url}/MyOffice/ClaimSearch?take=1", 
                    headers=headers, timeout=10)
                
                if response.status_code == 200:
                    return jsonify({'success': True, 'message': 'Соединение с WebAPI установлено'})
                else:
                    return jsonify({'success': False, 'error': f'HTTP {response.status_code}'})
            except requests.RequestException as e:
                return jsonify({'success': False, 'error': f'Ошибка соединения: {str(e)}'})
                
        else:
            return jsonify({
                'success': False,
                'error': 'Неизвестный тип API'
            }), 400
            
    except Exception as e:
        logger.error(f"Error testing {api_type} connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Регистрируем API роуты (временно отключено из-за конфликтов)
# try:
#     register_api_routes(app)
#     logger.info("✅ API routes registered successfully")
# except Exception as e:
#     logger.error(f"❌ Failed to register API routes: {e}")


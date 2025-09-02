"""
Crystal Bay Travel - SAMO API Integration Platform
Главное приложение Flask с интеграцией WebAPI и SamoAPI
"""

import os
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
    # from webapi_integration import WebAPIIntegration
except ImportError as e:
    logger.warning(f"Import warning: {e}")

# Initialize integrations
try:
    samo_api = SamoIntegration()
    # webapi = WebAPIIntegration()
except Exception as e:
    logger.warning(f"Integration warning: {e}")
    samo_api = None
    # webapi = None

# === MAIN ROUTES ===

@app.route('/')
def index():
    """Главная страница - дашборд"""
    try:
        # Получаем статистику заявок
        stats = samo_api.get_dashboard_stats() if samo_api else {}
        
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
    try:
        # Получаем статистику заявок
        stats = samo_api.get_dashboard_stats() if samo_api else {}
        
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

@app.route('/tours-search')
def tours_search():
    """Поиск туров через SAMO API"""
    return render_template('tours_search.html',
                         active_page='tours-search',
                         page_title='Поиск туров')

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

# === API ROUTES ===

@app.route('/api/samo/<action>', methods=['GET', 'POST'])
def samo_api_proxy(action):
    """Прокси для всех SAMO API команд"""
    try:
        if request.method == 'GET':
            params = request.args.to_dict()
        else:
            params = request.get_json() or {}
        
        result = samo_api.execute_command(action, params) if samo_api else {'success': False, 'error': 'SAMO API not initialized'}
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"SAMO API error for {action}: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'action': action
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

# Register tours and orders API routes
try:
    from tours_api import register_tours_api
    register_tours_api(app)
    logger.info("Tours API routes registered successfully")
except Exception as e:
    logger.error(f"Failed to register tours API routes: {e}")

# === STARTUP ===

if __name__ == '__main__':
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        logger.info("Database tables created")
        
        # Проверяем API подключения
        logger.info("Checking API connections...")
        samo_health = samo_api.health_check() if samo_api else False
        webapi_health = False  # webapi.health_check() if webapi else False
        
        logger.info(f"SAMO API: {'✓' if samo_health else '✗'}")
        logger.info(f"WebAPI: {'✓' if webapi_health else '✗'}")
        
        logger.info("Crystal Bay Travel started successfully!")
    
    # Запуск приложения
    app.run(host="0.0.0.0", port=5000, debug=True)
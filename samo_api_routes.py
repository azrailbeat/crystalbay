"""
API маршруты для работы с Crystal Bay SAMO API
Предоставляет веб-интерфейс для всех функций SAMO API
"""
import logging
from flask import request, jsonify, render_template
from datetime import datetime, timedelta
from crystal_bay_samo_api import get_crystal_bay_api

logger = logging.getLogger(__name__)

def register_samo_api_routes(app):
    """Регистрация маршрутов SAMO API"""
    
    # === ГЛАВНАЯ СТРАНИЦА SAMO API ===
    
    @app.route('/samo-api')
    def samo_api_dashboard():
        """Главная страница управления SAMO API"""
        return render_template('samo_api_dashboard.html')
    
    # === ТЕСТИРОВАНИЕ ===
    
    @app.route('/api/samo/test', methods=['GET'])
    def test_samo_connection():
        """Тестирование подключения к SAMO API"""
        try:
            api = get_crystal_bay_api()
            result = api.test_connection()
            return jsonify(result)
        except Exception as e:
            logger.error(f"Ошибка тестирования SAMO API: {e}")
            return jsonify({
                'success': False,
                'message': f'Ошибка: {str(e)}'
            }), 500
    
    # === СПРАВОЧНИКИ ===
    
    @app.route('/api/samo/townfroms', methods=['GET'])
    def get_townfroms():
        """Получить города отправления"""
        try:
            api = get_crystal_bay_api()
            result = api.get_townfroms()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/states', methods=['GET'])
    def get_samo_states():
        """Получить страны"""
        try:
            api = get_crystal_bay_api()
            result = api.get_states()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/currencies', methods=['GET'])
    def get_samo_currencies():
        """Получить валюты"""
        try:
            api = get_crystal_bay_api()
            result = api.get_currencies()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/hotels', methods=['GET'])
    def get_samo_hotels():
        """Получить отели"""
        try:
            api = get_crystal_bay_api()
            state_key = request.args.get('state_key')
            result = api.get_hotels(state_key)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/tours', methods=['GET'])
    def get_samo_tours():
        """Получить туры"""
        try:
            api = get_crystal_bay_api()
            result = api.get_tours()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ПОИСК ТУРОВ ===
    
    @app.route('/api/samo/search/prices', methods=['POST'])
    def search_tour_prices():
        """Поиск цен на туры"""
        try:
            api = get_crystal_bay_api()
            params = request.json or {}
            result = api.search_tour_prices(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/search/tours', methods=['POST'])
    def search_tours():
        """Детальный поиск туров"""
        try:
            api = get_crystal_bay_api()
            params = request.json or {}
            result = api.search_tours_detailed(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === БРОНИРОВАНИЯ ===
    
    @app.route('/api/samo/bookings', methods=['GET'])
    def get_samo_bookings():
        """Получить список бронирований"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            result = api.get_bookings(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>', methods=['GET'])
    def get_samo_booking_details(booking_id):
        """Получить детали бронирования"""
        try:
            api = get_crystal_bay_api()
            result = api.get_booking_details(booking_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings', methods=['POST'])
    def create_samo_booking():
        """Создать новое бронирование"""
        try:
            api = get_crystal_bay_api()
            booking_data = request.json or {}
            result = api.create_booking(booking_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>', methods=['PUT'])
    def update_samo_booking(booking_id):
        """Обновить бронирование"""
        try:
            api = get_crystal_bay_api()
            booking_data = request.json or {}
            result = api.update_booking(booking_id, booking_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/bookings/<booking_id>/cancel', methods=['POST'])
    def cancel_samo_booking(booking_id):
        """Отменить бронирование"""
        try:
            api = get_crystal_bay_api()
            data = request.json or {}
            reason = data.get('reason', '')
            result = api.cancel_booking(booking_id, reason)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === КЛИЕНТЫ ===
    
    @app.route('/api/samo/persons', methods=['POST'])
    def create_person():
        """Создать клиента"""
        try:
            api = get_crystal_bay_api()
            person_data = request.json or {}
            result = api.create_person(person_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/persons/<person_id>', methods=['GET'])
    def get_samo_person(person_id):
        """Получить данные клиента"""
        try:
            api = get_crystal_bay_api()
            result = api.get_person(person_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/persons/<person_id>', methods=['PUT'])
    def update_person(person_id):
        """Обновить данные клиента"""
        try:
            api = get_crystal_bay_api()
            person_data = request.json or {}
            result = api.update_person(person_id, person_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ОТЧЕТЫ ===
    
    @app.route('/api/samo/reports/sales', methods=['GET'])
    def get_sales_report():
        """Отчет по продажам"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
            result = api.get_sales_report(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/reports/financial', methods=['GET'])
    def get_financial_report():
        """Финансовый отчет"""
        try:
            api = get_crystal_bay_api()
            date_from = request.args.get('date_from', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            date_to = request.args.get('date_to', datetime.now().strftime('%Y-%m-%d'))
            result = api.get_financial_report(date_from, date_to)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ ===
    
    @app.route('/api/samo/services', methods=['GET'])
    def get_samo_services():
        """Получить дополнительные услуги"""
        try:
            api = get_crystal_bay_api()
            result = api.get_services()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/services/book', methods=['POST'])
    def book_service():
        """Забронировать дополнительную услугу"""
        try:
            api = get_crystal_bay_api()
            service_data = request.json or {}
            result = api.book_service(service_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # === ПЛАТЕЖИ ===
    
    @app.route('/api/samo/payments/methods', methods=['GET'])
    def get_payment_methods():
        """Получить способы оплаты"""
        try:
            api = get_crystal_bay_api()
            result = api.get_payment_methods()
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/payments', methods=['POST'])
    def create_payment():
        """Создать платеж"""
        try:
            api = get_crystal_bay_api()
            payment_data = request.json or {}
            result = api.create_payment(payment_data)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/samo/payments/<payment_id>/status', methods=['GET'])
    def get_payment_status(payment_id):
        """Получить статус платежа"""
        try:
            api = get_crystal_bay_api()
            result = api.get_payment_status(payment_id)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    logger.info("SAMO API routes registered successfully")